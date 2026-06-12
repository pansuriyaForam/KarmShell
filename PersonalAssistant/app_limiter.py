import psutil
import win32gui
import win32process
import time
from tkinter import messagebox

# Configuration: app name -> limit in minutes
limits = {
    "chrome.exe": 120,
    "discord.exe": 60,
    "spotify.exe": 90
}

# Track usage in seconds
usage = {app: 0 for app in limits}

# Track which warnings have been shown
warned_10min = set()
warned_5min = set()

# Blocked apps (in-memory, cleared on restart)
blocked_apps = set()


def get_active_window_process():
    """Get executable name of currently active window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name().lower()
    except:
        return None


def show_warning(title, message):
    """Display warning dialog."""
    try:
        messagebox.showwarning(title, message)
    except:
        print(f"{title}: {message}")


def terminate_app(app):
    """Terminate application and add to block list."""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == app:
                proc.kill()
        blocked_apps.add(app)
        show_warning("Limit Reached", f"{app} has been terminated.\nRestart computer to use again.")
    except:
        pass


def check_limits(app):
    """Check usage against limits and enforce accordingly."""
    if app in blocked_apps:
        return

    usage_minutes = usage[app] / 60
    limit_minutes = limits[app]

    # Terminate if limit reached
    if usage_minutes >= limit_minutes:
        terminate_app(app)
    # Warn at 5 minutes remaining
    elif usage_minutes >= limit_minutes - 5 and app not in warned_5min:
        show_warning("Warning", f"{app}: 5 minutes remaining")
        warned_5min.add(app)
    # Warn at 10 minutes remaining
    elif usage_minutes >= limit_minutes - 10 and app not in warned_10min:
        show_warning("Warning", f"{app}: 10 minutes remaining")
        warned_10min.add(app)


def monitor():
    """Main loop: check active app every second and accumulate usage."""
    while True:
        try:
            active_app = get_active_window_process()

            # Track usage for monitored apps
            if active_app in limits:
                usage[active_app] += 1
                check_limits(active_app)

            time.sleep(1)
        except:
            pass


if __name__ == "__main__":
    monitor()