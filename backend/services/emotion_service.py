import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

import os

# Download and load the custom emotion model from the public Hugging Face repository instead of the local hard drive
MODEL_PATH = "Krish0201/mental-health-emotion-model"

# Load once at startup (HuggingFace will automatically download and cache it locally)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

model.eval()

from models.emotion_labels import EMOTION_LABELS

def predict_emotion(text: str, top_k: int = 3):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=64
    )
    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.sigmoid(outputs.logits)[0].detach().numpy()

    # Build label → score dict
    emotion_scores = {label: float(probs[i]) for i, label in enumerate(EMOTION_LABELS)}

    # Sort and return top_k
    top_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    return {
        "top_emotions": [{"emotion": e, "score": round(s, 4)} for e, s in top_emotions],
        "all_scores": emotion_scores
    }
def get_concerning_emotions(text: str, threshold: float = 0.5):
    CONCERNING = {"grief", "fear", "sadness", "nervousness", "disgust", "remorse"}
    result = predict_emotion(text, top_k=28)
    return {
        e: s for e, s in result["all_scores"].items()
        if e in CONCERNING and s >= threshold
    }