import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import shutil
import ctypes


# Ensure logs directory exists
def ensure_logs_dir():
    Path("logs").mkdir(exist_ok=True)


# Delete temporary files from %TEMP%
def cleanup_temp():
    deleted_count = 0
    temp_path = Path(os.getenv("TEMP"))

    try:
        for item in temp_path.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                    deleted_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    deleted_count += 1
            except (PermissionError, OSError):
                # Skip files that cannot be deleted
                pass
    except Exception:
        pass

    return deleted_count


# Empty recycle bin
def empty_recycle_bin():
    try:
        # Call Windows API to empty recycle bin
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
        return "success"
    except Exception:
        return "failed"


# Flush DNS cache
def flush_dns_cache():
    try:
        result = subprocess.run(
            ["ipconfig", "/flushdns"],
            capture_output=True,
            text=True
        )
        return "success" if result.returncode == 0 else "failed"
    except Exception:
        return "failed"


# Save log to JSON file
def save_log(log_data):
    ensure_logs_dir()
    log_path = Path("logs/maintenance_log.json")

    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=4)


# Main execution
def main():
    # Run all maintenance tasks
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "recycle_bin": empty_recycle_bin(),
        "dns_cache_flush": flush_dns_cache()
    }

    # Save results to log
    save_log(log_data)
    print("Maintenance completed. Log saved to logs/maintenance_log.json")


if __name__ == "__main__":
    main()