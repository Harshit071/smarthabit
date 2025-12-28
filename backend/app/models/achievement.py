from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class AchievementType(str, enum.Enum):
    STREAK = "streak"
    COMPLETION = "completion"
    CONSISTENCY = "consistency"
    GOAL = "goal"
    SPECIAL = "special"


class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)  # Icon name or emoji
    achievement_type = Column(Enum(AchievementType), nullable=False)
    requirement_value = Column(Integer, nullable=False)  # e.g., 7 for 7-day streak
    xp_reward = Column(Integer, default=50)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")
    
    # Unique constraint: user can only unlock achievement once
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

