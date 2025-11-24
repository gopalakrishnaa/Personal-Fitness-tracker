import keyring

# Try to get from keyring first, fallback to env var (for backward compatibility/dev)
STRAVA_ACCESS_TOKEN = keyring.get_password("fitness_tracker", "strava_access_token")

if not STRAVA_ACCESS_TOKEN:
    import os
    STRAVA_ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
