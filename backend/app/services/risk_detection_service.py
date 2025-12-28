from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, timedelta
from typing import List
from app.models.habit import Habit, HabitStatus, HabitFrequency
from app.models.habit_log import HabitLog, LogStatus
from app.core.redis_client import publish_event


class RiskDetectionService:
    """Service for habit risk detection and adaptive suggestions"""
    
    @staticmethod
    def detect_at_risk_habits(db: Session, user_id: int) -> List[Habit]:
        """Detect habits that are at risk (2+ consecutive misses)"""
        habits = db.query(Habit).filter(
            and_(
                Habit.user_id == user_id,
                Habit.status == HabitStatus.ACTIVE
            )
        ).all()
        
        at_risk = []
        today = date.today()
        
        for habit in habits:
            # Check last 2 days
            yesterday = today - timedelta(days=1)
            day_before = today - timedelta(days=2)
            
            recent_logs = db.query(HabitLog).filter(
                and_(
                    HabitLog.habit_id == habit.id,
                    HabitLog.log_date.in_([yesterday, day_before])
                )
            ).all()
            
            missed_count = 0
            for check_date in [yesterday, day_before]:
                log = next((l for l in recent_logs if l.log_date == check_date), None)
                if not log or log.status != LogStatus.DONE:
                    missed_count += 1
            
            if missed_count >= 2:
                habit.status = HabitStatus.AT_RISK
                habit.consecutive_misses = missed_count
                at_risk.append(habit)
                
                # Publish risk alert
                publish_event(
                    channel=f"user:{user_id}",
                    event_type="habit_at_risk",
                    data={
                        "habit_id": habit.id,
                        "habit_name": habit.name,
                        "consecutive_misses": missed_count
                    },
                    user_id=user_id
                )
        
        db.commit()
        return at_risk
    
    @staticmethod
    def generate_adaptive_suggestions(db: Session, habit: Habit) -> dict:
        """Generate adaptive suggestions based on failure rate"""
        suggestions = {}
        
        # If failure rate is high, suggest reducing frequency
        if habit.failure_rate > 50 and habit.frequency == HabitFrequency.DAILY:
            suggestions["reduce_frequency"] = {
                "current": habit.frequency.value,
                "suggested": HabitFrequency.WEEKLY.value,
                "reason": f"High failure rate ({habit.failure_rate:.1f}%). Consider reducing frequency."
            }
            habit.suggested_frequency = HabitFrequency.WEEKLY
        
        # If consistency is low, suggest easier difficulty
        if habit.consistency_score < 30:
            suggestions["reduce_difficulty"] = {
                "current": habit.difficulty.value,
                "suggested": "easy",
                "reason": f"Low consistency score ({habit.consistency_score:.1f}%). Consider making the habit easier."
            }
        
        # If streak is broken, suggest restarting with smaller goals
        if habit.current_streak == 0 and habit.longest_streak > 0:
            suggestions["restart"] = {
                "message": "Your streak was broken. Don't worry! Start fresh with smaller, achievable goals.",
                "previous_streak": habit.longest_streak
            }
        
        db.commit()
        return suggestions
    
    @staticmethod
    def check_inactive_habits(db: Session, user_id: int, days_inactive: int = 7) -> List[Habit]:
        """Check for habits that haven't been logged in N days"""
        cutoff_date = date.today() - timedelta(days=days_inactive)
        
        habits = db.query(Habit).filter(
            and_(
                Habit.user_id == user_id,
                Habit.status == HabitStatus.ACTIVE
            )
        ).all()
        
        inactive = []
        for habit in habits:
            # Check if there's a log after cutoff date
            recent_log = db.query(HabitLog).filter(
                and_(
                    HabitLog.habit_id == habit.id,
                    HabitLog.log_date >= cutoff_date
                )
            ).first()
            
            if not recent_log:
                inactive.append(habit)
        
        return inactive

