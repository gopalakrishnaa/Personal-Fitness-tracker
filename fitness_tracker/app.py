import flet as ft
from .manager import FitnessManager
from .api import MockSensorAPI
from .views import Views

def main(page: ft.Page):
    page.title = "Fitness Tracker"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 800
    page.padding = 0
    
    manager = FitnessManager()
    api = MockSensorAPI()
    views = Views(page, manager, api)

    def change_tab(e):
        index = e.control.selected_index
        page.controls.clear()
        
        if index == 0:
            page.add(views.get_dashboard())
        elif index == 1:
            page.add(views.get_workout_view())
        elif index == 2:
            page.add(views.get_history_view())
        elif index == 3:
            page.add(views.get_goals_view())
            
        page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.DASHBOARD, label="Home"),
            ft.NavigationDestination(icon=ft.icons.DIRECTIONS_RUN, label="Workout"),
            ft.NavigationDestination(icon=ft.icons.HISTORY, label="History"),
            ft.NavigationDestination(icon=ft.icons.FLAG, label="Goals"),
        ],
        on_change=change_tab
    )

    # Initial view
    page.add(views.get_dashboard())

if __name__ == "__main__":
    ft.app(target=main)
