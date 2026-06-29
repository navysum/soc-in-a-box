from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from baseline import build_baseline, save_baseline, load_baseline
import argparse
from datetime import datetime
import hashlib
import json
import time
import os


MONITORED_PATH = os.getenv("MONITORED_PATH", "monitored")
REPORTS_PATH = os.getenv("REPORTS_PATH", "reports")
EVENT_LOG_FILE = os.path.join(REPORTS_PATH, "events.jsonl")
BASELINE_FILE = os.path.join(REPORTS_PATH, "baseline.json")


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_sha256(file_path):
    try:
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as file:
            for block in iter(lambda: file.read(4096), b""):
                sha256.update(block)

        return sha256.hexdigest()

    except FileNotFoundError:
        return None
    except PermissionError:
        return "PERMISSION_DENIED"


def get_severity(event_type):
    if event_type == "DELETED":
        return "CRITICAL"
    if event_type in ["MODIFIED", "MOVED"]:
        return "WARNING"
    return "INFO"


def save_event(event_data):
    os.makedirs(REPORTS_PATH, exist_ok=True)

    with open(EVENT_LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(event_data) + "\n")


class FileIntegrityHandler(FileSystemEventHandler):
    def handle_event(self, event_type, path, destination=None):
        if os.path.isdir(path):
            return

        timestamp = get_timestamp()
        file_hash = calculate_sha256(path)

        event_data = {
            "timestamp": timestamp,
            "event_type": event_type,
            "severity": get_severity(event_type),
            "path": path,
            "destination": destination,
            "sha256": file_hash,
        }

        save_event(event_data)

        message = (
            f"[{timestamp}] "
            f"[{event_data['severity']}] "
            f"[{event_type}] "
            f"{path}"
        )

        if destination:
            message += f" -> {destination}"

        if file_hash:
            message += f" | SHA256: {file_hash[:12]}..."

        print(message, flush=True)

    def on_created(self, event):
        if not event.is_directory:
            self.handle_event("CREATED", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.handle_event("MODIFIED", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.handle_event("DELETED", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.handle_event("MOVED", event.src_path, event.dest_path)


def main():
    parser = argparse.ArgumentParser(description="File Integrity Monitor")
    parser.add_argument(
        "--init-baseline",
        action="store_true",
        help="Create a trusted baseline of current file hashes",
    )

    args = parser.parse_args()

    os.makedirs(MONITORED_PATH, exist_ok=True)
    os.makedirs(REPORTS_PATH, exist_ok=True)

    if args.init_baseline:
        baseline = build_baseline(MONITORED_PATH)
        save_baseline(baseline, BASELINE_FILE)
        print(f"Baseline saved to: {BASELINE_FILE}", flush=True)
        return

    event_handler = FileIntegrityHandler()
    observer = Observer(timeout=0.5)
    observer.schedule(event_handler, MONITORED_PATH, recursive=True)
    observer.start()

    print(f"Monitoring folder: {MONITORED_PATH}", flush=True)
    print(f"Saving reports to: {EVENT_LOG_FILE}", flush=True)
    print(f"Using baseline file: {BASELINE_FILE}", flush=True)
    print("Press Ctrl+C to stop.", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping monitor...", flush=True)
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()