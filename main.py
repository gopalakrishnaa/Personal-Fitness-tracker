from fitness_tracker.cli import FitnessCLI

def main():
    app = FitnessCLI()
    try:
        app.main_menu()
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
