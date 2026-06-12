import json
import os
from datetime import datetime


def format_duration(seconds):
    """Convert seconds to 'X hours Y minutes' format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"


def load_json_file(filepath):
    """Load JSON file with error handling."""
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def ensure_logs_folder():
    """Create logs folder if it doesn't exist."""
    if not os.path.exists('logs'):
        os.makedirs('logs')


def process_activity_log(data):
    """Extract screen time and app usage from activity_tracker.json."""
    if not data or 'apps' not in data:
        return 0, {}

    total_seconds = 0
    app_durations = {}

    # data['apps'] is {app_name: [{duration_seconds: X}, ...]}
    for app_name, entries in data['apps'].items():
        if isinstance(entries, list):
            app_total = sum(entry.get('duration_seconds', 0) for entry in entries if isinstance(entry, dict))
            if app_total > 0:
                app_durations[app_name] = app_total
                total_seconds += app_total

    # Sort by duration descending
    sorted_apps = sorted(app_durations.items(), key=lambda x: x[1], reverse=True)
    return total_seconds, dict(sorted_apps)


def process_browser_log(data):
    """Extract website usage from browser_report.json."""
    if not data:
        return {}

    # data is {website: duration_seconds, ...}
    websites = {}

    for site, info in data.items():
        if isinstance(info, dict):
            websites[site] = info.get("time_seconds", 0)

    # Sort by duration descending and get top 10
    sorted_websites = sorted(websites.items(), key=lambda x: x[1], reverse=True)[:10]
    return dict(sorted_websites)


def display_summary(total_screen_time, apps, websites):
    """Display summary in terminal."""
    print("\n" + "=" * 60)
    print("DAILY SUMMARY")
    print("=" * 60)

    print(f"\nTotal Screen Time: {format_duration(total_screen_time)}")

    if apps:
        most_used_app = list(apps.keys())[0]
        print(f"Most Used Application: {most_used_app} ({format_duration(apps[most_used_app])})")

        print("\nApplication Durations:")
        for app, duration in apps.items():
            print(f"  {app}: {format_duration(duration)}")

    if websites:
        print("\nTop 10 Websites:")
        for website, duration in websites.items():
            print(f"  {website}: {format_duration(duration)}")

    print("\n" + "=" * 60 + "\n")


def save_summary(total_screen_time, apps, websites):
    """Save summary to logs/daily_summary.json."""
    summary = {
        'generated_at': datetime.now().isoformat(),
        'total_screen_time_seconds': total_screen_time,
        'total_screen_time_formatted': format_duration(total_screen_time),
        'applications': {app: {'duration_seconds': duration, 'duration_formatted': format_duration(duration)}
                         for app, duration in apps.items()},
        'top_websites': {website: {'duration_seconds': duration, 'duration_formatted': format_duration(duration)}
                         for website, duration in websites.items()}
    }

    try:
        with open('logs/daily_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Summary saved to logs/daily_summary.json")
    except Exception as e:
        print(f"Error saving summary: {e}")


def main():
    """Main function."""
    ensure_logs_folder()

    # Load data
    activity_data = load_json_file('logs/daily_activity.json')
    browser_data = load_json_file('logs/browser_report.json')

    # Process data
    total_screen_time, apps = process_activity_log(activity_data)
    websites = process_browser_log(browser_data)

    # Display and save
    display_summary(total_screen_time, apps, websites)
    save_summary(total_screen_time, apps, websites)


if __name__ == '__main__':
    main()