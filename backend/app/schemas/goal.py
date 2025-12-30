from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.habit import HabitResponse


class GoalBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_value: float
    unit: Optional[str] = None


class GoalCreate(GoalBase):
    habit_ids: Optional[List[int]] = None  # Habits that contribute to this goal
    contribution_weights: Optional[List[float]] = None


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    unit: Optional[str] = None
    habit_ids: Optional[List[int]] = None  # Add this for linking habits


class GoalHabitResponse(BaseModel):
    habit_id: int
    habit_name: str
    contribution_weight: float
    
    class Config:
        from_attributes = True


class GoalResponse(GoalBase):
    id: int
    user_id: int
    current_value: float
    is_completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    habit_contributions: Optional[List[GoalHabitResponse]] = None
    
    class Config:
        from_attributes = True

