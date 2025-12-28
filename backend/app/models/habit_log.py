from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class LogStatus(str, enum.Enum):
    DONE = "done"
    SKIPPED = "skipped"
    MISSED = "missed"


class HabitLog(Base):
    __tablename__ = "habit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    log_date = Column(Date, nullable=False, index=True)
    status = Column(Enum(LogStatus), nullable=False)
    notes = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    habit = relationship("Habit", back_populates="logs")
    
    # Unique constraint: one log per habit per date
    __table_args__ = (
        UniqueConstraint('habit_id', 'log_date', name='unique_habit_date'),
    )

