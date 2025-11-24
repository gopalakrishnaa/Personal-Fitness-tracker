import flet as ft
from dotenv import load_dotenv
from fitness_tracker.app import main

if __name__ == "__main__":
    load_dotenv()
    ft.app(target=main)
