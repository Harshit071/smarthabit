from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict
from app.database import get_db
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.core.security import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get overall dashboard statistics"""
    return AnalyticsService.get_user_dashboard_stats(db, current_user.id)


@router.get("/habits/{habit_id}/heatmap")
async def get_heatmap(
    habit_id: int,
    year: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get heatmap data for a habit"""
    # Verify habit belongs to user
    from app.services.habit_service import HabitService
    habit = HabitService.get_habit(db, habit_id, current_user.id)
    if not habit:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    return AnalyticsService.get_heatmap_data(db, current_user.id, habit_id, year)


@router.get("/habits/{habit_id}/weekly")
async def get_weekly_stats(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get weekly statistics for a habit"""
    from app.services.habit_service import HabitService
    habit = HabitService.get_habit(db, habit_id, current_user.id)
    if not habit:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    return AnalyticsService.get_weekly_stats(db, current_user.id, habit_id)


@router.get("/habits/{habit_id}/monthly")
async def get_monthly_stats(
    habit_id: int,
    year: int = None,
    month: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get monthly statistics for a habit"""
    from app.services.habit_service import HabitService
    habit = HabitService.get_habit(db, habit_id, current_user.id)
    if not habit:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    return AnalyticsService.get_monthly_stats(db, current_user.id, habit_id, year, month)


@router.get("/habits/{habit_id}/consistency-trend")
async def get_consistency_trend(
    habit_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get consistency trend over time"""
    from app.services.habit_service import HabitService
    habit = HabitService.get_habit(db, habit_id, current_user.id)
    if not habit:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    trend = AnalyticsService.get_consistency_trend(db, current_user.id, habit_id, days)
    return {"habit_id": habit_id, "days": days, "trend": trend}

