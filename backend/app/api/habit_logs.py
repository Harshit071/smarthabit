from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.habit_log import LogStatus
from app.schemas.habit_log import HabitLogCreate, HabitLogResponse
from app.services.habit_service import HabitService
from app.services.goal_service import GoalService
from app.core.security import get_current_user

router = APIRouter(prefix="/api/habit-logs", tags=["habit-logs"])


@router.post("", response_model=HabitLogResponse, status_code=status.HTTP_201_CREATED)
async def log_habit(
    log_data: HabitLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a habit (done/skipped/missed)"""
    log = HabitService.log_habit(
        db,
        log_data.habit_id,
        current_user.id,
        log_data.log_date,
        log_data.status,
        log_data.notes
    )
    
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    # Update goal progress if habit was completed
    if log_data.status == LogStatus.DONE:
        GoalService.update_goal_progress(db, log_data.habit_id)
    
    return log


@router.get("/habit/{habit_id}", response_model=List[HabitLogResponse])
async def get_habit_logs(
    habit_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get logs for a specific habit"""
    # Verify habit belongs to user
    habit = HabitService.get_habit(db, habit_id, current_user.id)
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    from app.models.habit_log import HabitLog
    query = db.query(HabitLog).filter(HabitLog.habit_id == habit_id)
    
    if start_date:
        query = query.filter(HabitLog.log_date >= start_date)
    if end_date:
        query = query.filter(HabitLog.log_date <= end_date)
    
    logs = query.order_by(HabitLog.log_date.desc()).all()
    return logs

