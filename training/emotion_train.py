import numpy as np
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    TrainerCallback
)
from sklearn.metrics import f1_score
import time

# -------------------------
# ⚙️ Config
# -------------------------
MODEL_NAME = "distilbert-base-uncased"
NUM_LABELS = 28          # 27 emotions + neutral
MAX_SEQ_LEN = 64         # GoEmotions texts are short; 64 is enough and faster than 128
TRAIN_BATCH  = 16        # larger batch = fewer steps = faster on CPU
EVAL_BATCH   = 32
NUM_EPOCHS   = 2
LEARNING_RATE = 2e-5
WEIGHT_DECAY  = 0.01

# Set to None to train on full dataset (takes ~6-12 hrs on CPU)

TRAIN_SUBSET = None
EVAL_SUBSET  = None


# -------------------------
# 1️⃣ Load Dataset
# -------------------------
print("📦 Loading dataset...")
dataset = load_dataset("go_emotions")

if TRAIN_SUBSET:
    print(f"⚡ Using subset: {TRAIN_SUBSET} train / {EVAL_SUBSET} eval samples")
    dataset["train"]      = dataset["train"].select(range(TRAIN_SUBSET))
    dataset["validation"] = dataset["validation"].select(range(EVAL_SUBSET))


# -------------------------
# 2️⃣ Tokenizer
# -------------------------
print("🔤 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


def tokenize_function(example):
    return tokenizer(
        example["text"],
        padding="max_length",
        truncation=True,
        max_length=MAX_SEQ_LEN
    )


dataset = dataset.map(tokenize_function, batched=True)


# -------------------------
# 3️⃣ Multi-hot label encoding
# -------------------------
def multi_hot_labels(example):
    multi_hot = np.zeros(NUM_LABELS, dtype=np.float32)  # float32 required for BCEWithLogitsLoss
    for label in example["labels"]:
        multi_hot[label] = 1
    example["labels"] = multi_hot
    return example


dataset = dataset.map(multi_hot_labels)
dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])


# -------------------------
# 4️⃣ Load Model
# -------------------------
print("🤖 Loading model...")
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=NUM_LABELS,
    problem_type="multi_label_classification"
)


# -------------------------
# 5️⃣ Metrics
# -------------------------
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = torch.sigmoid(torch.tensor(logits))
    predictions = (predictions > 0.5).int().numpy()
    labels = labels.astype(int)

    f1_micro = f1_score(labels, predictions, average="micro", zero_division=0)
    f1_macro = f1_score(labels, predictions, average="macro", zero_division=0)

    return {
        "f1_micro": f1_micro,
        "f1_macro": f1_macro
    }


# -------------------------
# 6️⃣ Progress Callback
# -------------------------
class ProgressCallback(TrainerCallback):
    def __init__(self):
        self.train_start = None

    def on_train_begin(self, args, state, control, **kwargs):
        self.train_start = time.time()
        print("\n🚀 Training started!\n")

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and "loss" in logs:
            elapsed = (time.time() - self.train_start) / 60
            step    = state.global_step
            total   = state.max_steps
            pct     = (step / total) * 100 if total else 0
            eta_min = (elapsed / pct * (100 - pct)) if pct > 0 else 0
            print(
                f"  Step {step}/{total} ({pct:.1f}%) | "
                f"Loss: {logs['loss']:.4f} | "
                f"Elapsed: {elapsed:.1f}m | "
                f"ETA: {eta_min:.1f}m"
            )

    def on_epoch_end(self, args, state, control, **kwargs):
        epoch = int(state.epoch)
        print(f"\n✅ Epoch {epoch} complete!\n")

    def on_train_end(self, args, state, control, **kwargs):
        total = (time.time() - self.train_start) / 60
        print(f"\n🎉 Training finished in {total:.1f} minutes!\n")


# -------------------------
# 7️⃣ Training Arguments
# -------------------------
training_args = TrainingArguments(
    output_dir="../ml_models/emotion_model",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=TRAIN_BATCH,
    per_device_eval_batch_size=EVAL_BATCH,
    num_train_epochs=NUM_EPOCHS,
    weight_decay=WEIGHT_DECAY,
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="f1_micro",
    greater_is_better=True,
    logging_dir="../logs",
    logging_steps=50,
    fp16=False,          # CPU doesn't support fp16
    dataloader_num_workers=0,  # 0 is safest on Windows
    report_to="none",    # disable wandb/tensorboard noise
)



# -------------------------
# 8️⃣ Trainer
# -------------------------
from transformers import DefaultDataCollator

class FloatLabelCollator(DefaultDataCollator):
    def __call__(self, features, return_tensors=None):
        batch = super().__call__(features, return_tensors=return_tensors)
        batch["labels"] = batch["labels"].float()  # ✅ force float32
        return batch
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    compute_metrics=compute_metrics,
    callbacks=[ProgressCallback()],
    data_collator=FloatLabelCollator()
)


# -------------------------
# 9️⃣ Train & Save
# -------------------------
print("⏳ Starting training (this may take a while on CPU)...")
trainer.train()

print("💾 Saving model...")
trainer.save_model("../ml_models/emotion_model")
tokenizer.save_pretrained("../ml_models/emotion_model")  # save tokenizer alongside model
print("✅ Done! Model saved to ../ml_models/emotion_model")