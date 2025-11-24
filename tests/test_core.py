import unittest
import os
import time
from datetime import datetime
from fitness_tracker.models import Goal, GoalType, GoalPeriod, WorkoutSession
from fitness_tracker.manager import FitnessManager, DATA_FILE
from fitness_tracker.api import MockSensorAPI

class TestFitnessTracker(unittest.TestCase):
    def setUp(self):
        # Clean up data file before each test
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        self.manager = FitnessManager(username="TestUser")

    def tearDown(self):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)

    def test_add_goal(self):
        goal = Goal(type=GoalType.STEPS, target_value=5000, period=GoalPeriod.DAILY)
        self.manager.add_goal(goal)
        self.assertEqual(len(self.manager.profile.goals), 1)
        self.assertEqual(self.manager.profile.goals[0].target_value, 5000)

    def test_add_workout_and_stats(self):
        session = WorkoutSession(
            activity_type="Running",
            start_time=datetime.now(),
            end_time=datetime.now(),
            summary={"total_steps": 1000, "avg_hr": 120}
        )
        self.manager.add_workout(session)
        
        stats = self.manager.get_today_stats()
        self.assertEqual(stats["steps"], 1000)

    def test_goal_progress(self):
        goal = Goal(type=GoalType.STEPS, target_value=2000, period=GoalPeriod.DAILY)
        self.manager.add_goal(goal)
        
        session = WorkoutSession(
            activity_type="Walking",
            start_time=datetime.now(),
            end_time=datetime.now(),
            summary={"total_steps": 1000}
        )
        self.manager.add_workout(session)
        
        goals_status = self.manager.check_goals()
        self.assertEqual(len(goals_status), 1)
        self.assertEqual(goals_status[0]["progress"], 50.0)
        self.assertFalse(goals_status[0]["achieved"])
        
        # Add another workout to hit the goal
        session2 = WorkoutSession(
            activity_type="Walking",
            start_time=datetime.now(),
            end_time=datetime.now(),
            summary={"total_steps": 1500}
        )
        self.manager.add_workout(session2)
        
        goals_status = self.manager.check_goals()
        self.assertTrue(goals_status[0]["achieved"])

    def test_mock_api(self):
        api = MockSensorAPI()
        data_received = []
        
        def callback(data):
            data_received.append(data)
            
        api.add_callback(callback)
        api.start_stream()
        time.sleep(2.5) # Should get ~2 updates
        api.stop_stream()
        
        self.assertTrue(len(data_received) >= 2)
        self.assertTrue(data_received[0]["heart_rate"] > 0)

if __name__ == '__main__':
    unittest.main()
