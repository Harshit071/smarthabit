from celery_app.celery_app import celery_app
from app.database import SessionLocal
from app.config import settings
from app.services.risk_detection_service import RiskDetectionService
from app.services.habit_service import HabitService
from app.models.user import User
from app.models.habit import Habit, HabitStatus
from app.websocket.manager import manager
from datetime import datetime
import asyncio


@celery_app.task
def detect_habit_risks():
    """Periodically detect habits at risk"""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        for user in users:
            RiskDetectionService.detect_at_risk_habits(db, user.id)
    finally:
        db.close()


@celery_app.task
def send_daily_nudges():
    """Send nudges to users with inactive habits"""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        for user in users:
            inactive_habits = RiskDetectionService.check_inactive_habits(db, user.id, days_inactive=2)
            
            if inactive_habits:
                # Send WebSocket notification
                asyncio.run(manager.broadcast_to_user(
                    user.id,
                    "nudge",
                    {
                        "message": f"You have {len(inactive_habits)} inactive habits",
                        "habits": [{"id": h.id, "name": h.name} for h in inactive_habits]
                    }
                ))
                
                # Send email if configured
                if settings.SMTP_HOST:
                    send_nudge_email(user, inactive_habits)
    finally:
        db.close()


@celery_app.task
def update_all_streaks():
    """Update streaks for all active habits"""
    db = SessionLocal()
    try:
        habits = db.query(Habit).filter(Habit.status == HabitStatus.ACTIVE).all()
        for habit in habits:
            HabitService._update_habit_stats(db, habit)
    finally:
        db.close()


def send_nudge_email(user: User, habits: list):
    """Send email nudge (placeholder - implement with aiosmtplib)"""
    # TODO: Implement email sending with aiosmtplib
    pass

