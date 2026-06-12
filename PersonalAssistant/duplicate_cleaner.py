import os
import hashlib
import json
import shutil
from pathlib import Path


# Compute SHA256 hash of a file
def compute_hash(file_path):
    try:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return None


# Scan directories and group by file size
def scan_directories(scan_paths, duplicates_folder):
    size_map = {}

    for scan_path in scan_paths:
        if not os.path.exists(scan_path):
            continue

        for root, dirs, files in os.walk(scan_path):
            # Skip Duplicates folder
            if duplicates_folder in root:
                continue

            for file in files:
                file_path = os.path.join(root, file)

                # Ignore files already in Duplicates
                if duplicates_folder in file_path:
                    continue

                try:
                    # Get file size
                    file_size = os.path.getsize(file_path)

                    if file_size not in size_map:
                        size_map[file_size] = []
                    size_map[file_size].append(file_path)
                except Exception:
                    pass

    return size_map


# Build hash map only for files with identical sizes
def build_hash_map(size_map):
    hash_map = {}

    # Only process size groups with multiple files
    for file_size, file_list in size_map.items():
        if len(file_list) > 1:
            for file_path in file_list:
                file_hash = compute_hash(file_path)
                if file_hash:
                    if file_hash not in hash_map:
                        hash_map[file_hash] = []
                    hash_map[file_hash].append(file_path)

    return hash_map


# Move duplicate files to Duplicates folder
def move_duplicates(hash_map, duplicates_folder):
    report = []

    for file_hash, file_list in hash_map.items():
        if len(file_list) > 1:
            # Keep first file, move rest
            original = file_list[0]

            for duplicate in file_list[1:]:
                try:
                    os.makedirs(duplicates_folder, exist_ok=True)

                    # Get just the filename
                    dup_filename = os.path.basename(duplicate)
                    dest_path = os.path.join(duplicates_folder, dup_filename)

                    # Handle name collisions in Duplicates folder
                    counter = 1
                    base_name, ext = os.path.splitext(dup_filename)
                    while os.path.exists(dest_path):
                        dest_path = os.path.join(duplicates_folder, f"{base_name}_{counter}{ext}")
                        counter += 1

                    shutil.move(duplicate, dest_path)

                    report.append({
                        "original": original,
                        "duplicate": duplicate,
                        "hash": file_hash
                    })
                except Exception:
                    pass

    return report


# Write JSON report
def write_report(report, logs_folder):
    try:
        os.makedirs(logs_folder, exist_ok=True)
        report_path = os.path.join(logs_folder, "duplicate_report.json")

        with open(report_path, 'w') as f:
            json.dump({"duplicates": report}, f, indent=4)
    except Exception:
        pass


# Main execution
def main():
    # Get user home directory
    home = str(Path.home())

    # Define scan paths for Windows 11
    scan_paths = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "Documents")
    ]

    # Define Duplicates and logs folders in script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    duplicates_folder = os.path.join(script_dir, "Duplicates")
    logs_folder = os.path.join(script_dir, "logs")

    # Scan directories and group by size
    size_map = scan_directories(scan_paths, duplicates_folder)

    # Build hash map only for files with identical sizes
    hash_map = build_hash_map(size_map)

    # Move duplicates and get report
    report = move_duplicates(hash_map, duplicates_folder)

    # Write report
    write_report(report, logs_folder)

    print(f"Scan complete. Found {len(report)} duplicates. Report saved to {logs_folder}/duplicate_report.json")


if __name__ == "__main__":
    main()