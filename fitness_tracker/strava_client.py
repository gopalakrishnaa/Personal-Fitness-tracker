import requests
from .models import WorkoutSession
from .config import STRAVA_ACCESS_TOKEN

class StravaClient:
    BASE_URL = "https://www.strava.com/api/v3"

    def __init__(self):
        self.token = STRAVA_ACCESS_TOKEN

    def upload_activity(self, session: WorkoutSession) -> dict:
        """
        Uploads a workout session to Strava.
        Returns the API response or raises an exception.
        """
        url = f"{self.BASE_URL}/activities"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Calculate duration in seconds
        duration = 0
        if session.end_time:
            duration = int((session.end_time - session.start_time).total_seconds())
        
        # Map activity type (Strava uses specific strings)
        # Defaulting to "Run" if not specified or "Running"
        strava_type = "Run"
        if session.activity_type.lower() == "walking":
            strava_type = "Walk"
        elif session.activity_type.lower() == "cycling":
            strava_type = "Ride"
            
        payload = {
            "name": f"{session.activity_type} Session",
            "type": strava_type,
            "start_date_local": session.start_time.isoformat(),
            "elapsed_time": duration,
            "description": f"Uploaded from Personal Fitness Tracker.\nSteps: {session.summary.get('total_steps', 0)}\nAvg HR: {int(session.summary.get('avg_hr', 0))}",
            "trainer": 0,
            "commute": 0
        }
        
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
