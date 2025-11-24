import json
import os
from datetime import datetime, date
from typing import List, Optional, Dict
from .models import UserProfile, Goal, WorkoutSession, GoalType, GoalPeriod

DATA_FILE = "fitness_data.json"

class FitnessManager:
    def __init__(self, username: str = "User"):
        self.username = username
        self.profile = UserProfile(username=username)
        self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                    self.profile = UserProfile.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                print("Error loading data, starting fresh.")

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.profile.to_dict(), f, indent=4)

    def add_goal(self, goal: Goal):
        self.profile.goals.append(goal)
        self.save_data()

    def add_workout(self, session: WorkoutSession):
        self.profile.workouts.append(session)
        self.save_data()

    def get_active_goals(self) -> List[Goal]:
        # Logic to filter active goals could be added here
        return self.profile.goals

    def get_today_stats(self) -> Dict[str, float]:
        today = date.today()
        stats = {
            "steps": 0,
            "calories": 0, # Not currently tracked in mock api but good to have structure
            "duration_minutes": 0
        }
        
        for workout in self.profile.workouts:
            if workout.start_time.date() == today:
                stats["steps"] += workout.summary.get("total_steps", 0)
                # stats["calories"] += workout.summary.get("calories", 0)
                
                if workout.end_time:
                    duration = (workout.end_time - workout.start_time).total_seconds() / 60
                    stats["duration_minutes"] += duration

        return stats

    def check_goals(self) -> List[Dict]:
        today_stats = self.get_today_stats()
        results = []
        
        for goal in self.profile.goals:
            if goal.period == GoalPeriod.DAILY:
                current = 0
                if goal.type == GoalType.STEPS:
                    current = today_stats["steps"]
                elif goal.type == GoalType.DURATION_MINUTES:
                    current = today_stats["duration_minutes"]
                
                # Simple percentage calculation
                progress = min(100, (current / goal.target_value) * 100) if goal.target_value > 0 else 0
                
                results.append({
                    "goal": goal,
                    "current": current,
                    "progress": progress,
                    "achieved": current >= goal.target_value
                })
        return results
