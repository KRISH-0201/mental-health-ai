from collections import Counter, defaultdict
from datetime import datetime
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import EmotionLog


def get_mood_summary(user_id: str):

    db: Session = SessionLocal()

    try:
        logs = db.query(EmotionLog).filter(
            EmotionLog.emotion.isnot(None),
            EmotionLog.user_id == user_id
        ).all()

        if not logs:
            return {"message": "No data available for this user."}

        total = len(logs)
        # Extract values while session is still open (avoids DetachedInstanceError)
        emotions = [log.emotion for log in logs]
        intensities = [log.intensity for log in logs]
    finally:
        db.close()

    emotion_counts = Counter(emotions)

    summary = {
        "total_logs": total,
        "emotion_distribution": dict(emotion_counts),
        "most_common_emotion": emotion_counts.most_common(1)[0][0],
        "average_intensity": round(sum(intensities) / total, 2),
    }

    return summary


def weekly_trend(user_id: str):

    db = SessionLocal()

    try:
        logs = db.query(EmotionLog).filter(
            EmotionLog.user_id == user_id
        ).all()
    finally:
        db.close()

    trend = defaultdict(int)

    for log in logs:
        week = log.timestamp.strftime("%Y-%U")  # Year-Week
        trend[week] += 1

    return dict(trend)


def emotion_percentage(user_id: str):

    db = SessionLocal()

    try:
        logs = db.query(EmotionLog).filter(
            EmotionLog.user_id == user_id
        ).all()
    finally:
        db.close()

    if not logs:
        return {}

    total = len(logs)
    counts: dict = {}

    for log in logs:
        emotion = log.emotion
        counts[emotion] = counts.get(emotion, 0) + 1

    percentages = {
        emotion: round((count / total) * 100, 2)
        for emotion, count in counts.items()
    }

    return percentages