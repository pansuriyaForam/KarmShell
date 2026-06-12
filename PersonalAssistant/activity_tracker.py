import json
import os
import time
from datetime import datetime
from pathlib import Path

import win32gui
import win32process

# Configuration
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "daily_activity.json")
CHECK_INTERVAL = 1

# Global state
current_app = None
app_start_time = None


def ensure_log_file():
    """Create logs folder if missing."""
    Path(LOG_DIR).mkdir(exist_ok=True)


def load_data():
    """Load existing activity data from JSON."""
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)

        # Check if date matches today
        today = datetime.now().strftime("%Y-%m-%d")
        if data.get("date") != today:
            # New day, reset with today's date
            return {"date": today, "apps": {}}

        return data
    except (FileNotFoundError, json.JSONDecodeError):
        today = datetime.now().strftime("%Y-%m-%d")
        return {"date": today, "apps": {}}


def save_data(data):
    """Save activity data to JSON."""
    try:
        # Ensure date is set to today
        data["date"] = datetime.now().strftime("%Y-%m-%d")
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")


def get_active_app():
    """Get the name of the currently active application."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return None

        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        if not pid:
            return None

        # Extract exe name from process
        import psutil
        try:
            proc = psutil.Process(pid)
            return proc.name()
        except:
            return None
    except Exception as e:
        return None


def record_session(app_name, start_time, end_time):
    """Record a completed application session."""
    if not app_name or not app_name.strip():
        return

    data = load_data()

    if app_name not in data["apps"]:
        data["apps"][app_name] = []

    duration = int((end_time - start_time).total_seconds())

    session = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration
    }

    data["apps"][app_name].append(session)
    save_data(data)


def main():
    """Main tracking loop."""
    global current_app, app_start_time

    ensure_log_file()
    print("Activity tracker started. Press Ctrl+C to stop.")

    try:
        while True:
            active_app = get_active_app()
            now = datetime.now()

            # Application changed
            if active_app != current_app:
                # Record previous session if exists
                if current_app and app_start_time:
                    record_session(current_app, app_start_time, now)

                # Start new session
                current_app = active_app
                app_start_time = now if active_app else None

                if active_app:
                    print(f"Switched to: {active_app}")

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        # Record final session on exit
        if current_app and app_start_time:
            record_session(current_app, app_start_time, datetime.now())
        print("\nActivity tracker stopped.")


if __name__ == "__main__":
    main()