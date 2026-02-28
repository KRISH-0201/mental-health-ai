from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import BurnoutScore, EmotionLog


NEGATIVE_EMOTIONS = {"sadness", "anxiety", "anger", "grief", "fear", "nervousness", "remorse", "disgust"}


def calculate_burnout_risk(user_id: str) -> dict:
    """
    Returns burnout score and risk level for a user.
    Uses BurnoutScore (cumulative) + EmotionLog (last 7 days) from DB.
    """
    db: Session = SessionLocal()

    try:
        # 1. Get stored burnout score
        burnout = db.query(BurnoutScore).filter_by(user_id=user_id).first()
        score = burnout.score if burnout else 0

        # 2. Count negative emotions in last 7 days from EmotionLog
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_logs = db.query(EmotionLog).filter(
            EmotionLog.user_id == user_id,
            EmotionLog.timestamp >= seven_days_ago
        ).all()

        total = len(recent_logs)
        negative_count = sum(1 for log in recent_logs if log.emotion in NEGATIVE_EMOTIONS)

        negative_ratio = round(negative_count / total, 2) if total > 0 else 0.0

        # Risk level based on stored burnout score
        if score >= 70:
            risk_level = "high"
        elif score >= 40:
            risk_level = "moderate"
        else:
            risk_level = "low"

        return {
            "burnout_score": score,
            "risk_level": risk_level,
            "negative_ratio": negative_ratio,
            "total_logs_7d": total,
        }
    finally:
        db.close()
