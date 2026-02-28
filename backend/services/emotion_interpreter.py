# -------------------------
# Emotion Categories
# -------------------------

NEGATIVE = {
    "sadness", "grief", "disappointment", "remorse",
    "anger", "fear", "nervousness", "disgust",
    "embarrassment", "anxiety", "anxious"
}

POSITIVE = {
    "joy", "love", "optimism", "gratitude",
    "excitement", "pride", "relief", "amusement",
    "happy"
}

CONCERNING = {
    "grief", "fear", "sadness", "nervousness",
    "remorse", "anxiety", "anxious"
}


# -------------------------
# Emotion Interpreter
# -------------------------

def interpret_emotions(top_emotions: list, threshold: float = 0.3):

    if not top_emotions:
        return {
            "sentiment": "neutral",
            "intensity": 0.0,
            "intensity_label": "low",
            "dominant_emotion": "neutral",
            "dominant_score": 0.0,
            "concerning_score": 0.0,
            "support_level": "normal"
        }

    dominant = top_emotions[0]["emotion"].lower()
    dominant_score = float(top_emotions[0]["score"])

    # -------------------------
    # Weighted Sentiment
    # -------------------------

    pos_score = sum(e["score"] for e in top_emotions if e["emotion"].lower() in POSITIVE)
    neg_score = sum(e["score"] for e in top_emotions if e["emotion"].lower() in NEGATIVE)

    margin = 0.1

    if neg_score - pos_score > margin and neg_score > threshold:
        sentiment = "negative"
    elif pos_score - neg_score > margin and pos_score > threshold:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    # -------------------------
    # Intensity (numeric + label)
    # -------------------------

    intensity_value = dominant_score

    if dominant_score >= 0.7:
        intensity_label = "high"
    elif dominant_score >= 0.4:
        intensity_label = "moderate"
    else:
        intensity_label = "low"

    # -------------------------
    # Concerning Score
    # -------------------------

    concerning_score = sum(
        e["score"] for e in top_emotions
        if e["emotion"].lower() in CONCERNING
    )

    # -------------------------
    # Support Level Logic
    # -------------------------

    if concerning_score >= 0.9:
        support_level = "crisis"
    elif concerning_score >= 0.6:
        support_level = "elevated"
    else:
        support_level = "normal"

    return {
        "sentiment": sentiment,
        "intensity": round(intensity_value, 4),   # numeric
        "intensity_label": intensity_label,       # readable
        "dominant_emotion": dominant,
        "dominant_score": round(dominant_score, 4),
        "concerning_score": round(concerning_score, 4),
        "support_level": support_level
    }