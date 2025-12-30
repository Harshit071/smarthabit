from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.goal import Goal, GoalHabit
from app.models.habit_log import LogStatus
from app.schemas.goal import GoalCreate, GoalUpdate
from app.core.redis_client import publish_event


class GoalService:
    """Service for goal-related business logic"""
    
    @staticmethod
    def create_goal(db: Session, user_id: int, goal_data: GoalCreate) -> Goal:
        """Create a new goal with optional habit contributions"""
        goal = Goal(
            user_id=user_id,
            name=goal_data.name,
            description=goal_data.description,
            target_value=goal_data.target_value,
            unit=goal_data.unit
        )
        db.add(goal)
        db.flush()
        
        # Add habit contributions
        if goal_data.habit_ids:
            weights = goal_data.contribution_weights or [1.0] * len(goal_data.habit_ids)
            for habit_id, weight in zip(goal_data.habit_ids, weights):
                goal_habit = GoalHabit(
                    goal_id=goal.id,
                    habit_id=habit_id,
                    contribution_weight=weight
                )
                db.add(goal_habit)
        
        db.commit()
        db.refresh(goal)
        return goal
    
    @staticmethod
    def get_goals(db: Session, user_id: int) -> List[Goal]:
        """Get all goals for a user"""
        return db.query(Goal).filter(Goal.user_id == user_id).order_by(Goal.created_at.desc()).all()
    
    @staticmethod
    def get_goal(db: Session, goal_id: int, user_id: int) -> Optional[Goal]:
        """Get a specific goal"""
        return db.query(Goal).filter(
            and_(Goal.id == goal_id, Goal.user_id == user_id)
        ).first()
    
    @staticmethod
    def update_goal(db: Session, goal_id: int, user_id: int, goal_data: GoalUpdate, habit_ids: Optional[List[int]] = None) -> Optional[Goal]:
        """Update a goal"""
        goal = GoalService.get_goal(db, goal_id, user_id)
        if not goal:
            return None
        
        update_data = goal_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)

        # Handle habit linking/unlinking
        if habit_ids is not None:
            # Clear existing habit links for this goal
            db.query(GoalHabit).filter(GoalHabit.goal_id == goal.id).delete()
            db.flush() # Flush to ensure deletions are processed before new insertions

            # Create new habit links
            for habit_id in habit_ids:
                # You might want to add a check here if the habit_id actually exists and belongs to the user
                goal_habit = GoalHabit(
                    goal_id=goal.id,
                    habit_id=habit_id,
                    contribution_weight=1.0 # Default weight, can be expanded later
                )
                db.add(goal_habit)
        
        db.commit()
        db.refresh(goal)
        return goal
    
    @staticmethod
    def delete_goal(db: Session, goal_id: int, user_id: int) -> bool:
        """Delete a goal"""
        goal = GoalService.get_goal(db, goal_id, user_id)
        if not goal:
            return False
        
        db.delete(goal)
        db.commit()
        return True
    
    @staticmethod
    def update_goal_progress(db: Session, habit_id: int):
        """Update goal progress when a habit is completed"""
        # Find all goals that include this habit
        goal_habits = db.query(GoalHabit).filter(GoalHabit.habit_id == habit_id).all()
        
        for goal_habit in goal_habits:
            goal = goal_habit.goal
            if goal.is_completed:
                continue
            
            # Recalculate current value based on all contributing habits
            total_contributions = 0.0
            
            for gh in goal.habit_contributions:
                # Count done logs for this habit
                from app.models.habit_log import HabitLog
                done_count = db.query(HabitLog).filter(
                    and_(
                        HabitLog.habit_id == gh.habit_id,
                        HabitLog.status == LogStatus.DONE
                    )
                ).count()
                
                total_contributions += done_count * gh.contribution_weight
            
            goal.current_value = total_contributions
            
            # Check if goal is completed
            if goal.current_value >= goal.target_value and not goal.is_completed:
                from datetime import datetime
                goal.is_completed = True
                goal.completed_at = datetime.utcnow()
                
                # Publish completion event
                publish_event(
                    channel=f"user:{goal.user_id}",
                    event_type="goal_completed",
                    data={
                        "goal_id": goal.id,
                        "goal_name": goal.name,
                        "current_value": goal.current_value,
                        "target_value": goal.target_value
                    },
                    user_id=goal.user_id
                )
            
            db.commit()
            db.refresh(goal)

