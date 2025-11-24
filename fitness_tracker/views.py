import flet as ft
from datetime import datetime
import time
import threading
from .manager import FitnessManager
from .models import Goal, GoalType, GoalPeriod, WorkoutSession

class Views:
    def __init__(self, page: ft.Page, manager: FitnessManager, api):
        self.page = page
        self.manager = manager
        self.api = api
        self.current_view = "dashboard"
        
        # State for workout
        self.workout_running = False
        self.workout_data = {"heart_rate": 0, "steps": 0, "elapsed": 0}
        self.workout_metrics = {"heart_rate": [], "steps": []}
        self.start_time = None

    def get_dashboard(self):
        stats = self.manager.get_today_stats()
        goals_status = self.manager.check_goals()
        
        # Progress Cards
        progress_controls = []
        if not goals_status:
            progress_controls.append(ft.Text("No goals set for today.", color=ft.colors.GREY))
        else:
            for item in goals_status:
                goal = item["goal"]
                progress_controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.FLAG, color=ft.colors.BLUE),
                                ft.Text(f"{goal.type.value.title()} ({goal.period.value})", weight=ft.FontWeight.BOLD),
                            ]),
                            ft.ProgressBar(value=min(1.0, item["progress"] / 100), color=ft.colors.BLUE),
                            ft.Text(f"{item['current']:.0f} / {goal.target_value} ({item['progress']:.1f}%)")
                        ]),
                        padding=10,
                        border=ft.border.all(1, ft.colors.OUTLINE),
                        border_radius=10,
                        margin=5
                    )
                )

        return ft.Column([
            ft.Text("Today's Dashboard", size=30, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Row([
                    self._stat_card("Steps", str(stats["steps"]), ft.icons.DIRECTIONS_WALK, ft.colors.ORANGE),
                    self._stat_card("Duration", f"{stats['duration_minutes']:.1f} m", ft.icons.TIMER, ft.colors.GREEN),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                padding=20
            ),
            ft.Divider(),
            ft.Text("Goals Progress", size=20, weight=ft.FontWeight.BOLD),
            ft.Column(progress_controls)
        ], scroll=ft.ScrollMode.AUTO)

    def _stat_card(self, title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=40, color=color),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                ft.Text(title, color=ft.colors.GREY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=15,
            width=150
        )

    def get_workout_view(self):
        self.timer_text = ft.Text("00:00", size=60, weight=ft.FontWeight.BOLD)
        self.hr_text = ft.Text("--", size=40, color=ft.colors.RED)
        self.steps_text = ft.Text("--", size=40, color=ft.colors.ORANGE)
        
        self.start_btn = ft.ElevatedButton("Start Workout", on_click=self.start_workout, icon=ft.icons.PLAY_ARROW, height=50)
        self.stop_btn = ft.ElevatedButton("Stop Workout", on_click=self.stop_workout, icon=ft.icons.STOP, height=50, disabled=True, color=ft.colors.ERROR)
        
        return ft.Column([
            ft.Text("Live Workout", size=30, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            ft.Container(
                content=ft.Column([
                    ft.Text("Duration", color=ft.colors.GREY),
                    self.timer_text
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center
            ),
            ft.Container(height=20),
            ft.Row([
                ft.Column([
                    ft.Icon(ft.icons.FAVORITE, color=ft.colors.RED, size=30),
                    self.hr_text,
                    ft.Text("BPM")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([
                    ft.Icon(ft.icons.DIRECTIONS_WALK, color=ft.colors.ORANGE, size=30),
                    self.steps_text,
                    ft.Text("Steps")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            ft.Container(height=40),
            ft.Row([self.start_btn, self.stop_btn], alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def start_workout(self, e):
        self.workout_running = True
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.start_time = datetime.now()
        self.workout_metrics = {"heart_rate": [], "steps": []}
        
        self.api.add_callback(self._update_workout_ui)
        self.api.start_stream()
        self.page.update()

    def stop_workout(self, e):
        self.workout_running = False
        self.api.stop_stream()
        
        end_time = datetime.now()
        
        # Save session
        session = WorkoutSession(
            activity_type="Running", # Default for now
            start_time=self.start_time,
            end_time=end_time,
            metrics=self.workout_metrics,
            summary={
                "total_steps": self.workout_data["steps"],
                "avg_hr": sum(self.workout_metrics["heart_rate"]) / len(self.workout_metrics["heart_rate"]) if self.workout_metrics["heart_rate"] else 0
            }
        )
        self.manager.add_workout(session)
        
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.timer_text.value = "00:00"
        self.hr_text.value = "--"
        self.steps_text.value = "--"
        
        self.page.snack_bar = ft.SnackBar(ft.Text("Workout Saved!"))
        self.page.snack_bar.open = True
        self.page.update()

    def _update_workout_ui(self, data):
        if not self.workout_running:
            return
            
        self.workout_data = data
        self.workout_metrics["heart_rate"].append(data["heart_rate"])
        self.workout_metrics["steps"].append(data["steps"])
        
        elapsed = int(data["elapsed_seconds"])
        mins, secs = divmod(elapsed, 60)
        
        self.timer_text.value = f"{mins:02d}:{secs:02d}"
        self.hr_text.value = str(data["heart_rate"])
        self.steps_text.value = str(data["steps"])
        self.page.update()

    def get_history_view(self):
        workouts = self.manager.profile.workouts
        items = []
        
        from .strava_client import StravaClient
        strava = StravaClient()

        def upload_to_strava(e):
            session_idx = e.control.data
            session = workouts[session_idx]
            
            try:
                strava.upload_activity(session)
                self.page.snack_bar = ft.SnackBar(ft.Text("Successfully uploaded to Strava!"))
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Upload failed: {str(ex)}"), bgcolor=ft.colors.ERROR)
                self.page.snack_bar.open = True
                self.page.update()

        for idx, w in enumerate(reversed(workouts)): # Newest first
            # Calculate original index because we are reversing
            original_idx = len(workouts) - 1 - idx
            
            duration = (w.end_time - w.start_time).total_seconds() / 60 if w.end_time else 0
            items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.FITNESS_CENTER),
                    title=ft.Text(f"{w.activity_type} - {w.start_time.strftime('%Y-%m-%d %H:%M')}"),
                    subtitle=ft.Text(f"Duration: {duration:.1f}m | Steps: {w.summary.get('total_steps', 0)}"),
                    trailing=ft.IconButton(
                        icon=ft.icons.CLOUD_UPLOAD, 
                        tooltip="Upload to Strava",
                        on_click=upload_to_strava,
                        data=original_idx
                    )
                )
            )
            
        return ft.ListView(controls=items, expand=True)

    def get_goals_view(self):
        # Simple goal setting form
        type_dropdown = ft.Dropdown(
            label="Goal Type",
            options=[
                ft.dropdown.Option("steps"),
                ft.dropdown.Option("duration_minutes"),
            ],
            value="steps"
        )
        target_field = ft.TextField(label="Target Value", keyboard_type=ft.KeyboardType.NUMBER)
        
        def save_goal(e):
            if not target_field.value:
                return
            
            goal = Goal(
                type=GoalType(type_dropdown.value),
                target_value=int(target_field.value),
                period=GoalPeriod.DAILY
            )
            self.manager.add_goal(goal)
            self.page.snack_bar = ft.SnackBar(ft.Text("Goal Saved!"))
            self.page.snack_bar.open = True
            self.page.update()

        return ft.Column([
            ft.Text("Set New Goal", size=30, weight=ft.FontWeight.BOLD),
            type_dropdown,
            target_field,
            ft.ElevatedButton("Save Goal", on_click=save_goal)
        ], padding=20)
