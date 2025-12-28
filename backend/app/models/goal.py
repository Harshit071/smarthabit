from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    target_value = Column(Float, nullable=False)  # Target number of completions
    current_value = Column(Float, default=0.0)
    unit = Column(String, nullable=True)  # e.g., "days", "times", "hours"
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="goals")
    habit_contributions = relationship("GoalHabit", back_populates="goal", cascade="all, delete-orphan")


class GoalHabit(Base):
    """Many-to-many relationship between Goals and Habits"""
    __tablename__ = "goal_habits"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    contribution_weight = Column(Float, default=1.0)  # How much each habit completion contributes
    
    # Relationships
    goal = relationship("Goal", back_populates="habit_contributions")
    habit = relationship("Habit", back_populates="goal_habits")

