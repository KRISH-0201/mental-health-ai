from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import ChatHistory
from collections import Counter


def get_mood_summary(user_id: str):

    db: Session = SessionLocal()

    chats = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).all()

    db.close()

    if not chats:
        return {"message": "No data available for this user."}

    total_messages = len(chats)

    sentiments = [chat.sentiment for chat in chats]
    emotions = [chat.dominant_emotion for chat in chats]
    support_levels = [chat.support_level for chat in chats]

    sentiment_counts = Counter(sentiments)
    emotion_counts = Counter(emotions)
    support_counts = Counter(support_levels)

    summary = {
        "total_messages": total_messages,
        "sentiment_distribution": dict(sentiment_counts),
        "dominant_emotion_distribution": dict(emotion_counts),
        "support_level_distribution": dict(support_counts),
        "most_common_emotion": emotion_counts.most_common(1)[0][0]
    }

    return summary
from collections import defaultdict
from datetime import datetime

def weekly_trend(user_id: str):

    db = SessionLocal()

    chats = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).all()

    db.close()

    trend = defaultdict(int)

    for chat in chats:
        week = chat.timestamp.strftime("%Y-%U")  # Year-Week
        trend[week] += 1

    return dict(trend)
def emotion_percentage(user_id: str):

    db = SessionLocal()

    chats = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).all()

    db.close()

    if not chats:
        return {}

    total = len(chats)

    counts = {}

    for chat in chats:
        emotion = chat.dominant_emotion
        counts[emotion] = counts.get(emotion, 0) + 1

    percentages = {
        emotion: round((count / total) * 100, 2)
        for emotion, count in counts.items()
    }

    return percentages