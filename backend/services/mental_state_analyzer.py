from services.emotion_service import predict_emotion
from services.emotion_interpreter import interpret_emotions
from services.risk_service import detect_risk
from services.response_service import generate_response


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
    response = generate_response(analysis)

    # Save to DB
    save_chat(user_id, text, analysis["emotion_analysis"])

    return {
        "analysis": analysis,
        "response": response
    }

from database.db import SessionLocal
from database.models import ChatHistory

def save_chat(user_id, text, emotion_analysis):

    db = SessionLocal()

    chat = ChatHistory(
        user_id=user_id,
        message=text,
        sentiment=emotion_analysis["sentiment"],
        dominant_emotion=emotion_analysis["dominant_emotion"],
        support_level=emotion_analysis["support_level"]
    )

    db.add(chat)
    db.commit()
    db.close()