from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from schemas.request_models import ChatRequest
from core.security import verify_token
from services.emotion_service import predict_emotion
from services.llm_service import generate_llm_response
from database.models import ChatHistory, EmotionLog, JournalEntry, MoodStreak, BurnoutScore
from database.db import SessionLocal

router = APIRouter()

# Emotions that reduce burnout score (positive)
POSITIVE_EMOTIONS = {"joy", "happiness", "relief", "gratitude", "amusement", "excitement", "love", "optimism", "pride"}

# Emotions that raise burnout score (negative)
EMOTION_WEIGHTS = {
    "sadness":     8,
    "anxiety":    10,
    "anger":       7,
    "grief":      12,
    "fear":        8,
    "nervousness": 6,
    "remorse":     5,
    "disgust":     5,
    "embarrassment": 4,
    "joy":        -5,
    "happiness":  -5,
    "relief":     -4,
    "gratitude":  -6,
    "amusement":  -3,
    "excitement": -3,
    "love":       -5,
    "optimism":   -4,
    "neutral":     0,
}

CRISIS_KEYWORDS = {"die", "suicide", "kill myself", "end my life", "want to die", "hurt myself"}


@router.post("/chat")
def chat_endpoint(data: ChatRequest, user=Depends(verify_token)):

    # ── Input Validation ─────────────────────────────────
    text = data.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="Message too long. Please keep it under 1000 characters.")

    db = SessionLocal()
    user_id = user.username
    user_message = text.lower()

    try:
        # ── Journal Mode ──────────────────────────────────
        if user_message.startswith("/journal"):
            db.add(JournalEntry(user_id=user_id, content=text))
            db.commit()
            return {
                "mode": "journal",
                "response": f"{user_id}, your thoughts have been saved safely. 🌿"
            }

        # ── Save User Message ─────────────────────────────
        db.add(ChatHistory(user_id=user_id, role="user", message=text))
        db.commit()

        # ── Emotion Detection ─────────────────────────────
        emotion_result   = predict_emotion(text)
        top_emotion_data = emotion_result["top_emotions"][0]
        dominant_emotion = top_emotion_data["emotion"]
        emotion_score    = int(top_emotion_data["score"] * 100)
        is_positive      = dominant_emotion in POSITIVE_EMOTIONS

        db.add(EmotionLog(user_id=user_id, emotion=dominant_emotion, intensity=emotion_score))
        db.commit()

        # ── Burnout Score Update ──────────────────────────
        burnout = db.query(BurnoutScore).filter_by(user_id=user_id).first()
        if not burnout:
            burnout = BurnoutScore(user_id=user_id, score=0)
            db.add(burnout)
            db.commit()

        is_crisis = any(kw in user_message for kw in CRISIS_KEYWORDS)
        adjustment = 25 if is_crisis else EMOTION_WEIGHTS.get(dominant_emotion, 0)
        burnout.score = max(0, min(100, burnout.score + adjustment))
        db.commit()

        # ── Generate Response ─────────────────────────────
        if is_crisis:
            response = (
                f"{user_id}, I'm really concerned about you right now.\n\n"
                "Please reach out — you don't have to face this alone:\n"
                "📞 iCALL: 9152987821\n"
                "📞 KIRAN: 1800-599-0019 (free, 24/7)\n"
                "📞 AASRA: +91-22-27546669\n\n"
                "You matter deeply. 💜"
            )
        else:
            # Build chat history context (last 6 messages)
            history = (
                db.query(ChatHistory)
                .filter(ChatHistory.user_id == user_id)
                .order_by(ChatHistory.timestamp.desc())
                .limit(6)
                .all()
            )

            # ── Context-Aware System Prompt ───────────────
            burnout_context = (
                "The user's burnout score is LOW — they are doing well emotionally."
                if burnout.score < 40 else
                "The user's burnout score is MODERATE — be gently supportive."
                if burnout.score < 70 else
                "The user's burnout score is HIGH — be very gentle, warm, and grounding."
            )

            system_prompt = f"""You are Solace, a compassionate AI mental health companion.
Always address the user as "{user_id}".

CURRENT CONTEXT:
- Detected emotion: {dominant_emotion} (score: {emotion_score}%)
- Emotional state: {"positive/happy" if is_positive else "needs support"}
- {burnout_context}

STRICT RULES — follow these exactly:
1. If the user's emotion is positive (joy, happy, grateful, excited etc.), CELEBRATE with them. DO NOT mention crisis resources, hotlines, or dark possibilities. Just be warm and uplifting.
2. Only mention helpline numbers if the user explicitly expresses thoughts of self-harm or hopelessness.
3. Keep responses SHORT (2–4 sentences max). No long paragraphs.
4. Be conversational, not clinical. Avoid therapy jargon.
5. Mirror the user's emotional tone — match positivity with positivity, sadness with gentleness.
6. Never project negative emotions onto the user if they seem fine."""

            messages = [{"role": "system", "content": system_prompt}]
            for chat in reversed(history):
                messages.append({"role": chat.role, "content": chat.message})

            response = generate_llm_response(messages)

        # ── Save Assistant Reply ──────────────────────────
        db.add(ChatHistory(user_id=user_id, role="assistant", message=response))
        db.commit()

        # ── Mood Streak Logic ─────────────────────────────
        today  = datetime.utcnow().date()
        streak = db.query(MoodStreak).filter_by(user_id=user_id).first()

        if not streak:
            streak = MoodStreak(user_id=user_id, streak_count=1, last_active=datetime.utcnow())
            db.add(streak)
        else:
            if streak.last_active.date() != today:
                streak.streak_count += 1
                streak.last_active = datetime.utcnow()

        db.commit()

        return {
            "emotion":       dominant_emotion,
            "emotion_score": emotion_score,
            "burnout_score": burnout.score,
            "streak":        streak.streak_count,
            "response":      response,
        }

    finally:
        db.close()        # Always release DB connection, even on error
