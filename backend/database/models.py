from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database.db import Base


# -------------------------
# User Model (IMPORTANT)
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


# -------------------------
# Chat History (Memory)
# -------------------------
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    role = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# -------------------------
# Emotion Logs (Daily Graph)
# -------------------------
class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    emotion = Column(String)
    intensity = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# -------------------------
# Journal Entries
# -------------------------
class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# -------------------------
# Mood Streak System
# -------------------------
class MoodStreak(Base):
    __tablename__ = "mood_streaks"

    user_id = Column(String, primary_key=True)
    streak_count = Column(Integer, default=1)
    last_active = Column(DateTime)

class BurnoutScore(Base):
    __tablename__ = "burnout_scores"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True)
    score = Column(Integer, default=0)