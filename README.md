# Personal Fitness Tracker (Mobile App)

A Python-based Mobile Application (using Flet) for tracking fitness goals and simulating workout sessions.

## Features

- **Mobile UI**: Responsive design that looks great on mobile and desktop.
- **Goal Setting**: Set daily targets for steps or duration.
- **Live Workout Tracking**: Real-time dashboard showing simulated Heart Rate and Steps.
- **History**: View past workout sessions.
- **Strava Integration**: Upload completed workouts to Strava with one click.
- **Progress Tracking**: Visual progress bars for your daily goals.

## Installation

1. Clone the repository or download the source code.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### Secure Setup (Recommended)
1. Run the setup script to securely store your Strava Access Token in your OS's credential manager:
   ```bash
   python setup_secrets.py
   ```
   Enter your token when prompted.

### Legacy Setup (.env)
Alternatively, you can use a `.env` file (not recommended for public repos):
1. Copy `.env.example` to `.env`.
2. Add your token to the file.

## Usage

Run the application using Python:

```bash
python main.py
```

The app will launch in a new window.

### Navigation
- Use the bottom navigation bar to switch between Home, Workout, History, and Goals.

## Project Structure

- `main.py`: Entry point.
- `fitness_tracker/`: Core package.
    - `app.py`: Main Flet application logic.
    - `views.py`: UI screens and components.
    - `models.py`: Data classes.
    - `api.py`: Mock Sensor API.
    - `manager.py`: Data management.

## Data Persistence
Data is saved locally to `fitness_data.json`. You can delete this file to reset your profile.
