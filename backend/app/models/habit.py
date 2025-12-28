from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class HabitFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class HabitDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class HabitPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HabitStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    AT_RISK = "at_risk"


class Habit(Base):
    __tablename__ = "habits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    frequency = Column(Enum(HabitFrequency), default=HabitFrequency.DAILY)
    difficulty = Column(Enum(HabitDifficulty), default=HabitDifficulty.MEDIUM)
    priority = Column(Enum(HabitPriority), default=HabitPriority.MEDIUM)
    status = Column(Enum(HabitStatus), default=HabitStatus.ACTIVE)
    
    # Tracking fields
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_completions = Column(Integer, default=0)
    total_skips = Column(Integer, default=0)
    consistency_score = Column(Float, default=0.0)  # 0-100
    
    # Risk detection
    consecutive_misses = Column(Integer, default=0)
    last_completed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Adaptive suggestions
    suggested_frequency = Column(Enum(HabitFrequency), nullable=True)
    failure_rate = Column(Float, default=0.0)  # Percentage of missed habits
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="habits")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")
    goal_habits = relationship("GoalHabit", back_populates="habit", cascade="all, delete-orphan")

