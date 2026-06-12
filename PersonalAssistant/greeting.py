#!/usr/bin/env python3
"""
greeting.py - Windows 11 Automated Greeting System
A production-grade automation script that delivers personalized greetings
with system information, ASCII art, and natural voice output.

Author: Windows Automation Engineer
Date: 2026
Platform: Windows 11+
"""

import json
import os
import sys
import subprocess
import random
from datetime import datetime
from pathlib import Path
import traceback

# Win32 voice support
try:
    import win32com.client

    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False


# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

def load_config():
    """
    Load configuration from config.json in script directory.
    Returns config dict with sensible defaults if file missing.
    """
    config_path = Path(__file__).parent / "config.json"

    default_config = {
        "name": "User",
        "use_voice": True,
        "voice_preference": "female",
        "randomize_voice": False,
        "speak_battery": True,
        "speak_wifi": True,
    }

    if not config_path.exists():
        print(f"[CONFIG] config.json not found at {config_path}, using defaults")
        return default_config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        # Merge with defaults to handle missing keys
        config = {**default_config, **user_config}
        print(f"[CONFIG] Loaded from {config_path}")
        return config
    except (json.JSONDecodeError, IOError) as e:
        print(f"[CONFIG] Error loading config: {e}. Using defaults.")
        return default_config


# ============================================================================
# SYSTEM INFORMATION COLLECTION
# ============================================================================

def get_battery_percentage():
    """
    Query Windows for battery percentage using wmic command.
    Returns int (0-100) or None if unavailable.
    """
    try:
        result = subprocess.run(
            ["wmic", "path", "Win32_Battery", "get", "EstimatedChargeRemaining"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return None

        # Parse output: first line is header, second line is value
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            battery_str = lines[1].strip()
            if battery_str.isdigit():
                return int(battery_str)
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"[BATTERY] Error querying battery: {e}")

    return None


def get_wifi_ssid():
    """
    Query WiFi SSID using netsh command.
    Returns SSID string or "offline" if unavailable.
    """
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return "offline"

        # Parse output for SSID field
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith("SSID"):
                # Format: "SSID : Network Name"
                parts = line.split(":")
                if len(parts) >= 2:
                    ssid = parts[1].strip()
                    # Skip empty or placeholder values
                    if ssid and ssid.lower() != "interface":
                        return ssid

        return "offline"
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"[WIFI] Error querying WiFi: {e}")

    return "offline"


def get_system_info():
    """
    Collect current system information.
    Returns dict with time, date, day_of_week, battery, and wifi.
    """
    now = datetime.now()

    info = {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "day_of_week": now.strftime("%A"),
        "battery": get_battery_percentage(),
        "wifi": get_wifi_ssid(),
        "timestamp": now.isoformat(),
    }

    return info


# ============================================================================
# ASCII ART MANAGEMENT
# ============================================================================

def load_ascii_art():
    """
    Load a random ASCII art file from assets/ directory.
    Returns ASCII art string or None if no files available.
    """
    assets_path = Path(__file__).parent / "assets"

    if not assets_path.exists():
        print("[ASCII] assets/ directory not found")
        return None

    try:
        ascii_files = list(assets_path.glob("*.txt"))

        if not ascii_files:
            print("[ASCII] No ASCII art files found in assets/")
            return None

        selected_file = random.choice(ascii_files)
        with open(selected_file, "r", encoding="utf-8") as f:
            ascii_art = f.read()

        print(f"[ASCII] Loaded: {selected_file.name}")
        return ascii_art
    except Exception as e:
        print(f"[ASCII] Error loading ASCII art: {e}")

    return None


# ============================================================================
# VOICE OUTPUT (WINDOWS SAPI)
# ============================================================================

def get_available_voices():
    """
    Enumerate available SAPI voices.
    Returns list of voice objects or empty list if unavailable.
    """
    if not HAS_WIN32COM:
        return []

    try:
        tts = win32com.client.Dispatch("SAPI.SpVoice")
        voices = tts.GetVoices()
        voice_list = []

        for voice in voices:
            voice_list.append({
                "name": voice.GetAttribute("Name"),
                "object": voice,
            })

        return voice_list
    except Exception as e:
        print(f"[VOICE] Error enumerating voices: {e}")

    return []


def select_voice(config, available_voices):
    """
    Select appropriate voice based on config preferences.
    Returns voice object or None.
    """
    if not available_voices:
        return None

    preference = config.get("voice_preference", "female").lower()
    randomize = config.get("randomize_voice", False)

    # If randomize enabled, just pick a random voice
    if randomize:
        selected = random.choice(available_voices)
        print(f"[VOICE] Selected random: {selected['name']}")
        return selected["object"]

    # Otherwise, find preferred voice
    female_voices = [v for v in available_voices if "female" in v["name"].lower()]
    male_voices = [v for v in available_voices if "male" in v["name"].lower()]

    if preference == "female" and female_voices:
        selected = female_voices[0]
        print(f"[VOICE] Selected female: {selected['name']}")
        return selected["object"]
    elif preference == "male" and male_voices:
        selected = male_voices[0]
        print(f"[VOICE] Selected male: {selected['name']}")
        return selected["object"]

    # Fallback: use first available
    selected = available_voices[0]
    print(f"[VOICE] Selected default: {selected['name']}")
    return selected["object"]


def speak_greeting(name, system_info, config):
    """
    Generate and speak natural greeting using Windows SAPI.
    Constructs greeting from system info based on config preferences.
    """
    if not config.get("use_voice", True):
        print("[VOICE] Voice output disabled in config")
        return

    if not HAS_WIN32COM:
        print("[VOICE] win32com.client not available, skipping voice output")
        return

    try:
        # Construct natural greeting message
        greeting = f"Good {get_time_period(system_info['time'])}, {name}. System is ready."

        # Optionally add system details
        details = []
        if config.get("speak_battery", True) and system_info["battery"] is not None:
            details.append(f"Battery at {system_info['battery']} percent")

        if config.get("speak_wifi", True) and system_info["wifi"] != "offline":
            details.append(f"Connected to {system_info['wifi']}")

        if details:
            greeting += " " + ". ".join(details) + "."

        # Initialize TTS
        tts = win32com.client.Dispatch("SAPI.SpVoice")

        # Select and apply voice
        available_voices = get_available_voices()
        voice = select_voice(config, available_voices)
        if voice:
            tts.Voice = voice

        # Speak greeting
        print(f"[VOICE] Speaking: {greeting}")
        tts.Speak(greeting)

    except Exception as e:
        print(f"[VOICE] Error speaking greeting: {e}")


def get_time_period(time_str):
    """
    Determine time period (morning, afternoon, evening) from HH:MM:SS.
    Returns appropriate greeting salutation.
    """
    hour = int(time_str.split(":")[0])

    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


# ============================================================================
# LOGGING
# ============================================================================

def ensure_log_directory():
    """
    Ensure logs/ directory exists in script directory.
    Creates directory if missing.
    """
    log_dir = Path(__file__).parent / "logs"

    try:
        log_dir.mkdir(exist_ok=True)
        return log_dir
    except Exception as e:
        print(f"[LOGGING] Error creating logs directory: {e}")
        return None


def log_event(name, system_info, event_type="boot_greeting"):
    """
    Log event to logs/greeting_log.json in structured JSON format.
    Appends to existing log file.
    """
    log_dir = ensure_log_directory()
    if not log_dir:
        return

    log_file = log_dir / "greeting_log.json"

    # Construct log entry
    log_entry = {
        "timestamp": system_info.get("timestamp", ""),
        "time": system_info.get("time", ""),
        "date": system_info.get("date", ""),
        "day_of_week": system_info.get("day_of_week", ""),
        "name": name,
        "battery": system_info.get("battery"),
        "wifi": system_info.get("wifi", ""),
        "event": event_type,
    }

    try:
        # Load existing log or start new one
        log_data = []
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                log_data = json.load(f)

        # Append new entry
        log_data.append(log_entry)

        # Write back to file (pretty-printed for readability)
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        print(f"[LOGGING] Event logged to {log_file}")
    except Exception as e:
        print(f"[LOGGING] Error writing log: {e}")


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def main():
    """
    Main entry point: orchestrate all components.
    Load config, gather system info, display ASCII, speak greeting, log event.
    """
    print("=" * 70)
    print("GREETING.PY - Windows 11 Greeting System")
    print("=" * 70)

    try:
        # Step 1: Load configuration
        print("\n[STARTUP] Loading configuration...")
        config = load_config()
        name = config.get("name", "User")

        # Step 2: Gather system information
        print("[STARTUP] Collecting system information...")
        system_info = get_system_info()

        print(f"  Time: {system_info['time']}")
        print(f"  Date: {system_info['date']} ({system_info['day_of_week']})")
        battery = system_info['battery']
        print(f"  Battery: {battery}%" if battery is not None else "  Battery: unknown")
        print(f"  WiFi: {system_info['wifi']}")

        # Step 3: Display ASCII art
        print("\n[STARTUP] Loading ASCII art...")
        ascii_art = load_ascii_art()
        if ascii_art:
            print("\n" + ascii_art + "\n")

        # Step 4: Construct and display text greeting
        print(f"\n[GREETING] {get_time_period(system_info['time']).capitalize()}, {name}!")
        print("[GREETING] System is ready.")

        # Step 5: Speak greeting
        print("\n[STARTUP] Initiating voice output...")
        speak_greeting(name, system_info, config)

        # Step 6: Log event
        print("\n[STARTUP] Logging event...")
        log_event(name, system_info)

        print("\n" + "=" * 70)
        print("[SUCCESS] Greeting sequence complete")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()