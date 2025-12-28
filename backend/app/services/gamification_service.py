from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date
from typing import List, Optional
from app.models.user import User
from app.models.habit import Habit, HabitDifficulty
from app.models.habit_log import HabitLog, LogStatus
from app.models.achievement import Achievement, UserAchievement, AchievementType


class GamificationService:
    """Service for gamification features: XP, levels, achievements"""
    
    # XP values based on difficulty
    XP_VALUES = {
        HabitDifficulty.EASY: 10,
        HabitDifficulty.MEDIUM: 20,
        HabitDifficulty.HARD: 30
    }
    
    # Streak bonus XP
    STREAK_BONUSES = {
        7: 50,   # 7-day streak bonus
        14: 100, # 2-week streak bonus
        30: 200, # 30-day streak bonus
        60: 500, # 60-day streak bonus
        100: 1000 # 100-day streak bonus
    }
    
    # Level calculation: XP needed for each level
    @staticmethod
    def xp_for_level(level: int) -> int:
        """Calculate XP needed for a level"""
        return level * 100  # 100 XP per level
    
    @staticmethod
    def calculate_level(total_xp: int) -> int:
        """Calculate user level based on total XP"""
        level = 1
        xp_needed = 0
        while xp_needed <= total_xp:
            level += 1
            xp_needed += GamificationService.xp_for_level(level)
        return max(1, level - 1)
    
    @staticmethod
    def xp_to_next_level(total_xp: int, current_level: int) -> int:
        """Calculate XP needed to reach next level"""
        xp_for_next = GamificationService.xp_for_level(current_level + 1)
        return max(0, xp_for_next - total_xp)
    
    @staticmethod
    def award_xp_for_habit(db: Session, user_id: int, habit: Habit) -> dict:
        """Award XP for completing a habit"""
        base_xp = GamificationService.XP_VALUES.get(habit.difficulty, 10)
        
        # Streak bonus
        streak_bonus = 0
        for streak_threshold, bonus in sorted(GamificationService.STREAK_BONUSES.items()):
            if habit.current_streak >= streak_threshold and habit.current_streak % streak_threshold == 0:
                streak_bonus = bonus
                break
        
        total_xp = base_xp + streak_bonus
        
        # Update user XP
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.total_xp += total_xp
            user.total_points += total_xp
            
            # Check for level up
            old_level = user.level
            user.level = GamificationService.calculate_level(user.total_xp)
            leveled_up = user.level > old_level
            
            db.commit()
            
            return {
                "xp_earned": total_xp,
                "base_xp": base_xp,
                "streak_bonus": streak_bonus,
                "total_xp": user.total_xp,
                "level": user.level,
                "leveled_up": leveled_up,
                "xp_to_next": GamificationService.xp_to_next_level(user.total_xp, user.level)
            }
        
        return {"xp_earned": 0}
    
    @staticmethod
    def check_achievements(db: Session, user_id: int, habit: Habit = None) -> List[dict]:
        """Check and unlock achievements for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        unlocked_achievements = []
        
        # Get all achievements
        all_achievements = db.query(Achievement).all()
        
        # Get user's unlocked achievements
        unlocked_ids = {ua.achievement_id for ua in db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()}
        
        for achievement in all_achievements:
            if achievement.id in unlocked_ids:
                continue
            
            should_unlock = False
            
            if achievement.achievement_type == AchievementType.STREAK:
                if habit and habit.current_streak >= achievement.requirement_value:
                    should_unlock = True
            
            elif achievement.achievement_type == AchievementType.COMPLETION:
                total_completions = db.query(func.sum(Habit.total_completions)).filter(
                    Habit.user_id == user_id
                ).scalar() or 0
                if total_completions >= achievement.requirement_value:
                    should_unlock = True
            
            elif achievement.achievement_type == AchievementType.CONSISTENCY:
                if habit and habit.consistency_score >= achievement.requirement_value:
                    should_unlock = True
            
            elif achievement.achievement_type == AchievementType.GOAL:
                from app.models.goal import Goal
                completed_goals = db.query(func.count(Goal.id)).filter(
                    and_(Goal.user_id == user_id, Goal.is_completed == True)
                ).scalar() or 0
                if completed_goals >= achievement.requirement_value:
                    should_unlock = True
            
            if should_unlock:
                # Unlock achievement
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
                db.add(user_achievement)
                
                # Award XP
                user.total_xp += achievement.xp_reward
                user.total_points += achievement.xp_reward
                user.level = GamificationService.calculate_level(user.total_xp)
                
                db.commit()
                
                unlocked_achievements.append({
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "icon": achievement.icon,
                    "xp_reward": achievement.xp_reward
                })
        
        return unlocked_achievements
    
    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> dict:
        """Get comprehensive gamification stats for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Get achievements
        achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).join(Achievement).all()
        
        # Get total habits
        total_habits = db.query(func.count(Habit.id)).filter(
            Habit.user_id == user_id
        ).scalar() or 0
        
        # Get total completions
        total_completions = db.query(func.sum(Habit.total_completions)).filter(
            Habit.user_id == user_id
        ).scalar() or 0
        
        return {
            "total_xp": user.total_xp,
            "level": user.level,
            "total_points": user.total_points,
            "xp_to_next_level": GamificationService.xp_to_next_level(user.total_xp, user.level),
            "total_achievements": len(achievements),
            "total_habits": total_habits,
            "total_completions": total_completions,
            "achievements": [
                {
                    "id": ua.achievement.id,
                    "name": ua.achievement.name,
                    "description": ua.achievement.description,
                    "icon": ua.achievement.icon,
                    "unlocked_at": ua.unlocked_at.isoformat() if ua.unlocked_at else None
                }
                for ua in achievements
            ]
        }
    
    @staticmethod
    def initialize_achievements(db: Session):
        """Initialize default achievements in the database"""
        achievements_data = [
            {"name": "First Steps", "description": "Complete your first habit", "icon": "🎯", "type": AchievementType.COMPLETION, "requirement": 1, "xp": 50},
            {"name": "Streak Starter", "description": "Maintain a 3-day streak", "icon": "🔥", "type": AchievementType.STREAK, "requirement": 3, "xp": 50},
            {"name": "Week Warrior", "description": "Maintain a 7-day streak", "icon": "⭐", "type": AchievementType.STREAK, "requirement": 7, "xp": 100},
            {"name": "Consistency King", "description": "Maintain a 30-day streak", "icon": "👑", "type": AchievementType.STREAK, "requirement": 30, "xp": 500},
            {"name": "Habit Hero", "description": "Complete 100 habits", "icon": "💪", "type": AchievementType.COMPLETION, "requirement": 100, "xp": 200},
            {"name": "Goal Crusher", "description": "Complete 5 goals", "icon": "🎯", "type": AchievementType.GOAL, "requirement": 5, "xp": 300},
            {"name": "Perfect Week", "description": "Achieve 100% consistency for a week", "icon": "✨", "type": AchievementType.CONSISTENCY, "requirement": 100, "xp": 150},
        ]
        
        for ach_data in achievements_data:
            existing = db.query(Achievement).filter(Achievement.name == ach_data["name"]).first()
            if not existing:
                achievement = Achievement(
                    name=ach_data["name"],
                    description=ach_data["description"],
                    icon=ach_data["icon"],
                    achievement_type=ach_data["type"],
                    requirement_value=ach_data["requirement"],
                    xp_reward=ach_data["xp"]
                )
                db.add(achievement)
        
        db.commit()

