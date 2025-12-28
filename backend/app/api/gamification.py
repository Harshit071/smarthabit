from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.gamification_service import GamificationService
from app.core.security import get_current_user

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


@router.get("/stats")
async def get_gamification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's gamification stats (XP, level, achievements)"""
    stats = GamificationService.get_user_stats(db, current_user.id)
    return stats


@router.post("/init-achievements")
async def initialize_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initialize default achievements (admin function)"""
    GamificationService.initialize_achievements(db)
    return {"message": "Achievements initialized"}

