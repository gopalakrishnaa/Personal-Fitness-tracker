import time
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.align import Align
from rich import box

from .manager import FitnessManager
from .models import Goal, GoalType, GoalPeriod, WorkoutSession
from .api import MockSensorAPI

console = Console()

class FitnessCLI:
    def __init__(self):
        self.manager = FitnessManager()
        self.api = MockSensorAPI()

    def main_menu(self):
        while True:
            console.clear()
            console.print(Panel.fit("[bold cyan]Personal Fitness Tracker[/bold cyan]", border_style="cyan"))
            
            self.show_dashboard()
            
            console.print("\n[bold]Options:[/bold]")
            console.print("1. Start Workout")
            console.print("2. Set Goal")
            console.print("3. View History")
            console.print("4. Exit")
            
            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                self.start_workout()
            elif choice == "2":
                self.set_goal()
            elif choice == "3":
                self.view_history()
            elif choice == "4":
                console.print("Goodbye!")
                break

    def show_dashboard(self):
        goals_status = self.manager.check_goals()
        
        table = Table(title="Daily Goals Progress", box=box.ROUNDED)
        table.add_column("Goal", style="cyan")
        table.add_column("Target", style="magenta")
        table.add_column("Current", style="green")
        table.add_column("Progress", style="yellow")
        table.add_column("Status", justify="center")

        if not goals_status:
            table.add_row("-", "-", "-", "-", "No goals set")
        else:
            for item in goals_status:
                goal = item["goal"]
                status_icon = "✅" if item["achieved"] else "🏃"
                table.add_row(
                    f"{goal.type.value} ({goal.period.value})",
                    str(goal.target_value),
                    f"{item['current']:.1f}",
                    f"{item['progress']:.1f}%",
                    status_icon
                )
        
        console.print(table)

    def start_workout(self):
        console.clear()
        console.print(Panel("[bold green]Starting Workout...[/bold green]"))
        
        activity_type = Prompt.ask("Enter activity type", default="Running")
        
        self.api.start_stream()
        start_time = datetime.now()
        
        # Live display layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="metrics"),
            Layout(name="footer", size=3)
        )
        
        layout["header"].update(Panel(f"Activity: [bold]{activity_type}[/bold]", style="green"))
        layout["footer"].update(Panel("Press Ctrl+C to stop workout", style="red"))
        
        metrics_data = {"heart_rate": [], "steps": []}
        current_data = {"heart_rate": 0, "steps": 0, "elapsed": 0}

        def update_data(data):
            current_data["heart_rate"] = data["heart_rate"]
            current_data["steps"] = data["steps"]
            current_data["elapsed"] = data["elapsed_seconds"]
            
            metrics_data["heart_rate"].append(data["heart_rate"])
            metrics_data["steps"].append(data["steps"])

        self.api.add_callback(update_data)

        try:
            with Live(layout, refresh_per_second=4) as live:
                while True:
                    # Update metrics panel
                    m_table = Table.grid(expand=True)
                    m_table.add_column(justify="center", ratio=1)
                    m_table.add_column(justify="center", ratio=1)
                    m_table.add_column(justify="center", ratio=1)
                    
                    m_table.add_row(
                        Panel(f"[bold size=30]{int(current_data['elapsed'])}s[/bold]\nDuration", border_style="blue"),
                        Panel(f"[bold size=30]{current_data['heart_rate']}[/bold]\nBPM", border_style="red"),
                        Panel(f"[bold size=30]{current_data['steps']}[/bold]\nSteps", border_style="yellow")
                    )
                    
                    layout["metrics"].update(m_table)
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.api.stop_stream()
            end_time = datetime.now()
            
            # Save session
            session = WorkoutSession(
                activity_type=activity_type,
                start_time=start_time,
                end_time=end_time,
                metrics=metrics_data,
                summary={
                    "total_steps": current_data["steps"],
                    "avg_hr": sum(metrics_data["heart_rate"]) / len(metrics_data["heart_rate"]) if metrics_data["heart_rate"] else 0
                }
            )
            self.manager.add_workout(session)
            console.print("\n[bold green]Workout Saved![/bold green]")
            time.sleep(2)

    def set_goal(self):
        console.clear()
        console.print(Panel("[bold]Set a New Goal[/bold]"))
        
        g_type_str = Prompt.ask("Goal Type", choices=["steps", "duration_minutes"], default="steps")
        g_type = GoalType(g_type_str)
        
        target = IntPrompt.ask("Target Value")
        
        goal = Goal(
            type=g_type,
            target_value=target,
            period=GoalPeriod.DAILY # Simplified for now
        )
        
        self.manager.add_goal(goal)
        console.print("[green]Goal set successfully![/green]")
        time.sleep(1)

    def view_history(self):
        console.clear()
        table = Table(title="Workout History")
        table.add_column("Date")
        table.add_column("Activity")
        table.add_column("Duration (min)")
        table.add_column("Steps")
        table.add_column("Avg HR")
        
        for w in self.manager.profile.workouts:
            duration = (w.end_time - w.start_time).total_seconds() / 60 if w.end_time else 0
            steps = w.summary.get("total_steps", 0)
            avg_hr = w.summary.get("avg_hr", 0)
            
            table.add_row(
                w.start_time.strftime("%Y-%m-%d %H:%M"),
                w.activity_type,
                f"{duration:.1f}",
                str(steps),
                f"{avg_hr:.0f}"
            )
            
        console.print(table)
        Prompt.ask("\nPress Enter to return")
