# Personal Fitness Tracker

A Python-based CLI application for tracking fitness goals and simulating workout sessions with live data.

## Features

- **Goal Setting**: Set daily targets for steps or duration.
- **Live Workout Tracking**: Real-time dashboard showing simulated Heart Rate and Steps.
- **History**: View past workout sessions and performance stats.
- **Progress Tracking**: Visual dashboard to see how close you are to your daily goals.
- **Mock Sensor API**: Simulates realistic sensor data for development and testing.

## Installation

1. Clone the repository or download the source code.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application using Python:

```bash
python main.py
```

### Navigation
- Use the number keys to select menu options.
- Follow the on-screen prompts to set goals or start workouts.
- Press `Ctrl+C` to stop an active workout session.

## Project Structure

- `main.py`: Entry point of the application.
- `fitness_tracker/`: Core package.
    - `models.py`: Data classes for Goals, Workouts, and User Profile.
    - `api.py`: Mock API for generating sensor data.
    - `manager.py`: Handles data persistence and business logic.
    - `cli.py`: User interface implementation using `rich`.
- `tests/`: Automated tests.

## Data Persistence
Data is saved locally to `fitness_data.json`. You can delete this file to reset your profile.
