from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, timedelta
from typing import Dict, List
from app.models.habit import Habit
from app.models.habit_log import HabitLog, LogStatus


class AnalyticsService:
    """Service for analytics and reporting"""
    
    @staticmethod
    def get_heatmap_data(db: Session, user_id: int, habit_id: int, year: int = None) -> Dict:
        """Get heatmap data for a habit (GitHub-style contribution graph)"""
        if year is None:
            year = date.today().year
        
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        # Get all logs for the year
        logs = db.query(HabitLog).filter(
            and_(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date >= start_date,
                HabitLog.log_date <= end_date,
                HabitLog.status == LogStatus.DONE
            )
        ).all()
        
        # Create a dictionary of dates to counts
        heatmap_data = {}
        for log in logs:
            date_str = log.log_date.isoformat()
            heatmap_data[date_str] = heatmap_data.get(date_str, 0) + 1
        
        return {
            "year": year,
            "data": heatmap_data
        }
    
    @staticmethod
    def get_weekly_stats(db: Session, user_id: int, habit_id: int) -> Dict:
        """Get weekly statistics for a habit"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        logs = db.query(HabitLog).filter(
            and_(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date >= week_start,
                HabitLog.log_date <= week_end
            )
        ).all()
        
        stats = {
            "done": 0,
            "skipped": 0,
            "missed": 0
        }
        
        for log in logs:
            if log.status == LogStatus.DONE:
                stats["done"] += 1
            elif log.status == LogStatus.SKIPPED:
                stats["skipped"] += 1
            elif log.status == LogStatus.MISSED:
                stats["missed"] += 1
        
        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "stats": stats
        }
    
    @staticmethod
    def get_monthly_stats(db: Session, user_id: int, habit_id: int, year: int = None, month: int = None) -> Dict:
        """Get monthly statistics for a habit"""
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month
        
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
        
        logs = db.query(HabitLog).filter(
            and_(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date >= month_start,
                HabitLog.log_date <= month_end
            )
        ).all()
        
        stats = {
            "done": 0,
            "skipped": 0,
            "missed": 0
        }
        
        for log in logs:
            if log.status == LogStatus.DONE:
                stats["done"] += 1
            elif log.status == LogStatus.SKIPPED:
                stats["skipped"] += 1
            elif log.status == LogStatus.MISSED:
                stats["missed"] += 1
        
        return {
            "year": year,
            "month": month,
            "month_start": month_start.isoformat(),
            "month_end": month_end.isoformat(),
            "stats": stats
        }
    
    @staticmethod
    def get_consistency_trend(db: Session, user_id: int, habit_id: int, days: int = 30) -> List[Dict]:
        """Get consistency trend over time"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Group logs by date
        logs = db.query(
            func.date(HabitLog.log_date).label('date'),
            func.count(HabitLog.id).filter(HabitLog.status == LogStatus.DONE).label('done')
        ).filter(
            and_(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date >= start_date,
                HabitLog.log_date <= end_date
            )
        ).group_by(func.date(HabitLog.log_date)).all()
        
        trend = []
        for log_date, done_count in logs:
            trend.append({
                "date": log_date.isoformat(),
                "completions": done_count
            })
        
        return trend
    
    @staticmethod
    def get_user_dashboard_stats(db: Session, user_id: int) -> Dict:
        """Get overall dashboard statistics for a user"""
        habits = db.query(Habit).filter(Habit.user_id == user_id).all()
        
        total_habits = len(habits)
        active_habits = len([h for h in habits if h.status.value == "active"])
        at_risk_habits = len([h for h in habits if h.status.value == "at_risk"])
        
        total_streak = sum(h.current_streak for h in habits)
        avg_consistency = sum(h.consistency_score for h in habits) / total_habits if total_habits > 0 else 0
        
        # Get today's completions
        today = date.today()
        today_logs = db.query(HabitLog).join(Habit).filter(
            and_(
                Habit.user_id == user_id,
                HabitLog.log_date == today,
                HabitLog.status == LogStatus.DONE
            )
        ).count()
        
        return {
            "total_habits": total_habits,
            "active_habits": active_habits,
            "at_risk_habits": at_risk_habits,
            "total_streak": total_streak,
            "average_consistency": round(avg_consistency, 2),
            "today_completions": today_logs
        }

