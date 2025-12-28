from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from app.database import get_db
from app.models.user import User
from app.services.risk_detection_service import RiskDetectionService
from app.services.habit_service import HabitService
from app.core.security import get_current_user

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


@router.get("/habits/{habit_id}/adaptive")
async def get_adaptive_suggestions(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get adaptive suggestions for a habit"""
    habit = HabitService.get_habit(db, habit_id, current_user.id)
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    suggestions = RiskDetectionService.generate_adaptive_suggestions(db, habit)
    return {
        "habit_id": habit_id,
        "suggestions": suggestions
    }


@router.post("/detect-risks")
async def detect_risks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Manually trigger risk detection for all user habits"""
    at_risk = RiskDetectionService.detect_at_risk_habits(db, current_user.id)
    return {
        "at_risk_count": len(at_risk),
        "habits": [{"id": h.id, "name": h.name} for h in at_risk]
    }

