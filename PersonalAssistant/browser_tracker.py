import os
import json
import time
from urllib.parse import urlparse

import psutil
import win32gui
import win32process
from pywinauto import Application

LOG_DIR = "logs"
REPORT_FILE = os.path.join(LOG_DIR, "browser_report.json")

SUPPORTED = {
    "chrome.exe": "Chrome",
    "brave.exe": "Brave",
    "msedge.exe": "Edge"
}


def create_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def load_report():
    try:
        with open(REPORT_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_report(data):
    with open(REPORT_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_foreground_process():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        return proc.name().lower()
    except:
        return None


def get_current_url(browser_name):
    try:
        app = Application(backend="uia")

        app.connect(title_re=f".*{browser_name}.*")

        dlg = app.top_window()

        address_bar = dlg.child_window(
            title="Address and search bar",
            control_type="Edit"
        )

        return address_bar.get_value()

    except:
        return None


def extract_domain(url):
    try:
        if not url:
            return None

        parsed = urlparse(url)

        domain = parsed.netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except:
        return None


def main():

    create_log_dir()

    data = load_report()

    save_report(data)

    last_save = time.time()

    print("Browser tracker started.")

    try:

        while True:

            process = get_foreground_process()

            if process in SUPPORTED:

                browser_name = SUPPORTED[process]

                url = get_current_url(browser_name)

                domain = extract_domain(url)

                print("Process:", process)
                print("URL:", url)
                print("Domain:", domain)
                print("-------------------")

                if domain:

                    if domain not in data:
                        data[domain] = {
                            "time_seconds": 0
                        }

                    data[domain]["time_seconds"] += 1

            if time.time() - last_save >= 10:
                save_report(data)
                last_save = time.time()

            time.sleep(1)

    except KeyboardInterrupt:

        save_report(data)

        print("\nTracker stopped.")


if __name__ == "__main__":
    main()