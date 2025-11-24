from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class GoalType(Enum):
    STEPS = "steps"
    CALORIES = "calories"
    DURATION_MINUTES = "duration_minutes"

class GoalPeriod(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"

@dataclass
class Goal:
    type: GoalType
    target_value: int
    period: GoalPeriod
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            "type": self.type.value,
            "target_value": self.target_value,
            "period": self.period.value,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            type=GoalType(data["type"]),
            target_value=data["target_value"],
            period=GoalPeriod(data["period"]),
            created_at=datetime.fromisoformat(data["created_at"])
        )

@dataclass
class WorkoutSession:
    activity_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    metrics: Dict[str, List[float]] = field(default_factory=dict) # e.g., {'heart_rate': [80, 82...], 'steps': [0, 10...]}
    summary: Dict[str, float] = field(default_factory=dict) # e.g., {'total_steps': 1000, 'avg_hr': 120}

    def to_dict(self):
        return {
            "activity_type": self.activity_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "metrics": self.metrics,
            "summary": self.summary
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            activity_type=data["activity_type"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            metrics=data.get("metrics", {}),
            summary=data.get("summary", {})
        )

@dataclass
class UserProfile:
    username: str
    goals: List[Goal] = field(default_factory=list)
    workouts: List[WorkoutSession] = field(default_factory=list)

    def to_dict(self):
        return {
            "username": self.username,
            "goals": [g.to_dict() for g in self.goals],
            "workouts": [w.to_dict() for w in self.workouts]
        }

    @classmethod
    def from_dict(cls, data):
        profile = cls(username=data["username"])
        profile.goals = [Goal.from_dict(g) for g in data.get("goals", [])]
        profile.workouts = [WorkoutSession.from_dict(w) for w in data.get("workouts", [])]
        return profile
