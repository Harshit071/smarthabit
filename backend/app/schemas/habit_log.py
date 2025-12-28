from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from app.models.habit_log import LogStatus


class HabitLogBase(BaseModel):
    log_date: date
    status: LogStatus
    notes: Optional[str] = None


class HabitLogCreate(HabitLogBase):
    habit_id: int


class HabitLogResponse(HabitLogBase):
    id: int
    habit_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

