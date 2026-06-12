import subprocess
import sys
import os


def script_exists(filename):
    """Check if script file exists in the same directory."""
    return os.path.isfile(filename)


def start_script(filename):
    """Start a Python script using subprocess.Popen."""
    try:
        subprocess.Popen([sys.executable, filename])
        print(f"Started: {filename}")
    except Exception as e:
        print(f"Error starting {filename}: {e}")


def main():
    """Start all tracker scripts independently."""
    scripts = [
        "greeting.py",
        "activity_tracker.py",
        "browser_tracker.py",
        "app_limiter.py"
    ]

    # Launch each script
    for script in scripts:
        if script_exists(script):
            start_script(script)
        else:
            print(f"Missing: {script}")


if __name__ == "__main__":
    main()