from services.emotion_service import predict_emotion
from services.emotion_interpreter import interpret_emotions
from services.risk_service import detect_risk
from database.db import SessionLocal
from database.models import ChatHistory


def save_chat(user_id, text, emotion_analysis):

    db = SessionLocal()

    try:
        chat = ChatHistory(
            user_id=user_id,
            role="user",
            message=text,
        )
        db.add(chat)
        db.commit()
    finally:
        db.close()  # always release connection even if commit fails


def analyze_mental_state(text: str):

    emotions = predict_emotion(text)
    emotion_analysis = interpret_emotions(emotions["top_emotions"])

    risk_analysis = detect_risk(text)

    # Risk override logic
    if risk_analysis["risk_level"] == "high":
        emotion_analysis["support_level"] = "crisis"

    elif risk_analysis["risk_level"] == "moderate" and emotion_analysis["support_level"] == "normal":
        emotion_analysis["support_level"] = "elevated"

    return {
        "emotion_analysis": emotion_analysis,
        "risk_analysis": risk_analysis
    }


def analyze_and_respond(text: str, user_id="default_user"):

    analysis = analyze_mental_state(text)

    # Build a simple rule-based response since response_service doesn't exist
    emotion_analysis = analysis["emotion_analysis"]
    risk_level = analysis["risk_analysis"]["risk_level"]

    if risk_level == "high":
        response = (
            "I'm really concerned about you right now. "
            "Please reach out — you don't have to face this alone:\n"
            "📞 iCALL: 9152987821\n"
            "📞 KIRAN: 1800-599-0019 (free, 24/7)\n"
            "📞 AASRA: +91-22-27546669\n\n"
            "You matter deeply. 💜"
        )
    elif emotion_analysis["sentiment"] == "positive":
        response = "That's wonderful to hear! Keep embracing those positive feelings. 🌟"
    else:
        response = (
            f"I can sense you're feeling {emotion_analysis['dominant_emotion']}. "
            "I'm here for you — take your time and share what's on your mind. 💜"
        )

    # Save to DB
    save_chat(user_id, text, emotion_analysis)

    return {
        "analysis": analysis,
        "response": response
    }