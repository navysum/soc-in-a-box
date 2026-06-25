from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import hashlib
import json
import time
import os


MONITORED_PATH = os.getenv("MONITORED_PATH", "monitored")
REPORTS_PATH = os.getenv("REPORTS_PATH", "reports")
EVENT_LOG_FILE = os.path.join(REPORTS_PATH, "events.jsonl")


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

        event_data = {
            "timestamp": get_timestamp(),
            "event_type": event_type,
            "severity": get_severity(event_type),
            "path": path,
            "destination": destination,
            "sha256": calculate_sha256(path),
        }

        save_event(event_data)

        print(
            f"[{event_data['timestamp']}] "
            f"[{event_data['severity']}] "
            f"[{event_type}] "
            f"{path}",
            flush=True,
        )

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
    os.makedirs(MONITORED_PATH, exist_ok=True)
    os.makedirs(REPORTS_PATH, exist_ok=True)

    event_handler = FileIntegrityHandler()
    observer = Observer()
    observer.schedule(event_handler, MONITORED_PATH, recursive=True)
    observer.start()

    print(f"Monitoring folder: {MONITORED_PATH}", flush=True)
    print(f"Saving reports to: {EVENT_LOG_FILE}", flush=True)
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