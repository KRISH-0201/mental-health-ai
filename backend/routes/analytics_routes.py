from fastapi import APIRouter, Depends
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from database.db import SessionLocal
from database.models import EmotionLog
from core.security import verify_token
from services.analytics_service import get_mood_summary, emotion_percentage

router = APIRouter()


@router.get("/weekly-wellness")
def get_weekly_wellness(user=Depends(verify_token)):
    """
    Returns last-7-day average emotion intensity per day.
    Frontend uses this to power the Weekly Wellness spline chart.
    """
    db = SessionLocal()
    user_id = user.username

    today = datetime.utcnow().date()
    result = []

    try:
        for i in range(6, -1, -1):          # Mon → Sun (oldest → newest)
            day = today - timedelta(days=i)
            day_start = datetime(day.year, day.month, day.day)
            day_end   = day_start + timedelta(days=1)

            logs = db.query(EmotionLog).filter(
                EmotionLog.user_id == user_id,
                EmotionLog.timestamp >= day_start,
                EmotionLog.timestamp <  day_end,
            ).all()

            if logs:
                avg_intensity = round(sum(log.intensity for log in logs) / len(logs), 1)
            else:
                avg_intensity = None          # Frontend will keep last known value

            result.append({
                "day": day.strftime("%a"),    # "Mon", "Tue", …
                "value": avg_intensity,
            })
    finally:
        db.close()

    return result


@router.get("/mood-summary")
def mood_summary(user=Depends(verify_token)):
    """Returns full mood summary for the authenticated user."""
    return get_mood_summary(user.username)


@router.get("/emotion-percentage")
def emotion_pct(user=Depends(verify_token)):
    """Returns per-emotion percentage breakdown for the authenticated user."""
    return emotion_percentage(user.username)


@router.get("/daily-emotions/{user_id}")
def get_daily_emotions(user_id: str):
    """Legacy endpoint — grouped emotion counts per day."""
    db = SessionLocal()
    try:
        results = (
            db.query(
                func.date(EmotionLog.timestamp),
                EmotionLog.emotion,
                func.count()
            )
            .filter(EmotionLog.user_id == user_id)
            .group_by(func.date(EmotionLog.timestamp), EmotionLog.emotion)
            .all()
        )
        return results
    finally:
        db.close()
