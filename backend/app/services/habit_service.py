from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, datetime, timedelta
from typing import List, Optional
from app.models.habit import Habit, HabitStatus
from app.models.habit_log import HabitLog, LogStatus
from app.schemas.habit import HabitCreate, HabitUpdate
from app.core.redis_client import publish_event, cache_get, cache_set, get_cache_key


class HabitService:
    """Service for habit-related business logic"""
    
    @staticmethod
    def create_habit(db: Session, user_id: int, habit_data: HabitCreate) -> Habit:
        """Create a new habit"""
        habit = Habit(user_id=user_id, **habit_data.dict())
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return habit
    
    @staticmethod
    def get_habits(db: Session, user_id: int, status: Optional[HabitStatus] = None) -> List[Habit]:
        """Get all habits for a user"""
        query = db.query(Habit).filter(Habit.user_id == user_id)
        if status:
            query = query.filter(Habit.status == status)
        return query.order_by(Habit.created_at.desc()).all()
    
    @staticmethod
    def get_habit(db: Session, habit_id: int, user_id: int) -> Optional[Habit]:
        """Get a specific habit"""
        return db.query(Habit).filter(
            and_(Habit.id == habit_id, Habit.user_id == user_id)
        ).first()
    
    @staticmethod
    def update_habit(db: Session, habit_id: int, user_id: int, habit_data: HabitUpdate) -> Optional[Habit]:
        """Update a habit"""
        habit = HabitService.get_habit(db, habit_id, user_id)
        if not habit:
            return None
        
        update_data = habit_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(habit, field, value)
        
        db.commit()
        db.refresh(habit)
        return habit
    
    @staticmethod
    def delete_habit(db: Session, habit_id: int, user_id: int) -> bool:
        """Delete a habit"""
        habit = HabitService.get_habit(db, habit_id, user_id)
        if not habit:
            return False
        
        db.delete(habit)
        db.commit()
        return True
    
    @staticmethod
    def log_habit(db: Session, habit_id: int, user_id: int, log_date: date, status: LogStatus, notes: Optional[str] = None) -> Optional[HabitLog]:
        """Log a habit completion/skip/miss"""
        # Verify habit belongs to user
        habit = HabitService.get_habit(db, habit_id, user_id)
        if not habit:
            return None
        
        # Check if log already exists
        existing_log = db.query(HabitLog).filter(
            and_(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date == log_date
            )
        ).first()
        
        if existing_log:
            existing_log.status = status
            existing_log.notes = notes
            db.commit()
            db.refresh(existing_log)
            log = existing_log
        else:
            log = HabitLog(habit_id=habit_id, log_date=log_date, status=status, notes=notes)
            db.add(log)
            db.commit()
            db.refresh(log)
        
        # Update habit statistics
        HabitService._update_habit_stats(db, habit)
        
        # Gamification: Award XP and check achievements if habit is completed
        xp_data = {}
        achievements = []
        if status == LogStatus.DONE:
            from app.services.gamification_service import GamificationService
            xp_data = GamificationService.award_xp_for_habit(db, user_id, habit)
            achievements = GamificationService.check_achievements(db, user_id, habit)
        
        # Publish real-time event
        event_data = {
            "habit_id": habit_id,
            "habit_name": habit.name,
            "log_date": str(log_date),
            "status": status.value,
            "streak": habit.current_streak
        }
        
        # Add gamification data if available
        if xp_data:
            event_data["xp_earned"] = xp_data.get("xp_earned", 0)
            event_data["level"] = xp_data.get("level", 1)
            event_data["leveled_up"] = xp_data.get("leveled_up", False)
            event_data["total_xp"] = xp_data.get("total_xp", 0)
        
        if achievements:
            event_data["achievements_unlocked"] = achievements
        
        publish_event(
            channel=f"user:{user_id}",
            event_type="habit_logged",
            data=event_data,
            user_id=user_id
        )
        
        return log
    
    @staticmethod
    def _update_habit_stats(db: Session, habit: Habit):
        """Update habit statistics (streak, consistency, etc.)"""
        # Count logs
        total_logs = db.query(func.count(HabitLog.id)).filter(
            HabitLog.habit_id == habit.id
        ).scalar()
        
        done_logs = db.query(func.count(HabitLog.id)).filter(
            and_(
                HabitLog.habit_id == habit.id,
                HabitLog.status == LogStatus.DONE
            )
        ).scalar()
        
        skipped_logs = db.query(func.count(HabitLog.id)).filter(
            and_(
                HabitLog.habit_id == habit.id,
                HabitLog.status == LogStatus.SKIPPED
            )
        ).scalar()
        
        habit.total_completions = done_logs
        habit.total_skips = skipped_logs
        
        # Calculate streak
        streak = HabitService._calculate_streak(db, habit)
        habit.current_streak = streak
        if streak > habit.longest_streak:
            habit.longest_streak = streak
        
        # Calculate consistency score (last 30 days)
        consistency = HabitService._calculate_consistency_score(db, habit)
        habit.consistency_score = consistency
        
        # Update last completed date
        last_done = db.query(HabitLog).filter(
            and_(
                HabitLog.habit_id == habit.id,
                HabitLog.status == LogStatus.DONE
            )
        ).order_by(HabitLog.log_date.desc()).first()
        
        if last_done:
            habit.last_completed_date = datetime.combine(last_done.log_date, datetime.min.time())
        
        # Calculate failure rate
        if total_logs > 0:
            habit.failure_rate = (skipped_logs / total_logs) * 100
        else:
            habit.failure_rate = 0.0
        
        # Check for consecutive misses
        HabitService._check_consecutive_misses(db, habit)
        
        db.commit()
        db.refresh(habit)
    
    @staticmethod
    def _calculate_streak(db: Session, habit: Habit) -> int:
        """Calculate current streak of completed habits"""
        # Get all done logs ordered by date descending
        done_logs = db.query(HabitLog).filter(
            and_(
                HabitLog.habit_id == habit.id,
                HabitLog.status == LogStatus.DONE
            )
        ).order_by(HabitLog.log_date.desc()).all()
        
        if not done_logs:
            return 0
        
        streak = 0
        today = date.today()
        expected_date = today
        
        for log in done_logs:
            if log.log_date == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            elif log.log_date < expected_date:
                # Gap found, streak broken
                break
        
        return streak
    
    @staticmethod
    def _calculate_consistency_score(db: Session, habit: Habit, days: int = 30) -> float:
        """Calculate consistency score for last N days (0-100)"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Count expected days (based on frequency)
        if habit.frequency.value == "daily":
            expected_days = days
        elif habit.frequency.value == "weekly":
            expected_days = days // 7
        else:
            expected_days = days // 7  # Default to weekly
        
        # Count actual completions
        completions = db.query(func.count(HabitLog.id)).filter(
            and_(
                HabitLog.habit_id == habit.id,
                HabitLog.status == LogStatus.DONE,
                HabitLog.log_date >= start_date,
                HabitLog.log_date <= end_date
            )
        ).scalar()
        
        if expected_days == 0:
            return 0.0
        
        score = (completions / expected_days) * 100
        return min(100.0, max(0.0, score))
    
    @staticmethod
    def _check_consecutive_misses(db: Session, habit: Habit):
        """Check for consecutive missed days and update risk status"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        day_before = today - timedelta(days=2)
        
        # Check last 2 days
        recent_logs = db.query(HabitLog).filter(
            and_(
                HabitLog.habit_id == habit.id,
                HabitLog.log_date.in_([yesterday, day_before])
            )
        ).all()
        
        missed_count = 0
        for log_date in [yesterday, day_before]:
            log = next((l for l in recent_logs if l.log_date == log_date), None)
            if not log or log.status != LogStatus.DONE:
                missed_count += 1
        
        habit.consecutive_misses = missed_count
        
        # Mark as at risk if 2 consecutive misses
        if missed_count >= 2 and habit.status == HabitStatus.ACTIVE:
            habit.status = HabitStatus.AT_RISK
            # Publish risk alert
            publish_event(
                channel=f"user:{habit.user_id}",
                event_type="habit_at_risk",
                data={
                    "habit_id": habit.id,
                    "habit_name": habit.name,
                    "consecutive_misses": missed_count
                },
                user_id=habit.user_id
            )
        elif missed_count < 2 and habit.status == HabitStatus.AT_RISK:
            habit.status = HabitStatus.ACTIVE

