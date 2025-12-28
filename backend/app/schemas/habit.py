from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from app.models.habit import HabitFrequency, HabitDifficulty, HabitPriority, HabitStatus


class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: HabitFrequency = HabitFrequency.DAILY
    difficulty: HabitDifficulty = HabitDifficulty.MEDIUM
    priority: HabitPriority = HabitPriority.MEDIUM


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[HabitFrequency] = None
    difficulty: Optional[HabitDifficulty] = None
    priority: Optional[HabitPriority] = None
    status: Optional[HabitStatus] = None


class HabitResponse(HabitBase):
    id: int
    user_id: int
    status: HabitStatus
    current_streak: int
    longest_streak: int
    total_completions: int
    total_skips: int
    consistency_score: float
    consecutive_misses: int
    last_completed_date: Optional[datetime] = None
    suggested_frequency: Optional[HabitFrequency] = None
    failure_rate: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

