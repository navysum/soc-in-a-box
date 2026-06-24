from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import time
import os


MONITORED_PATH = os.getenv("MONITORED_PATH", "monitored")


class FileIntegrityHandler(FileSystemEventHandler):
    def log_event(self, event_type, path):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{event_type}] {path}", flush=True)

    def on_created(self, event):
        if not event.is_directory:
            self.log_event("CREATED", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.log_event("MODIFIED", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.log_event("DELETED", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.log_event("MOVED", f"{event.src_path} -> {event.dest_path}")


def main():
    if not os.path.exists(MONITORED_PATH):
        os.makedirs(MONITORED_PATH)

    event_handler = FileIntegrityHandler()
    observer = Observer()
    observer.schedule(event_handler, MONITORED_PATH, recursive=True)
    observer.start()

    print(f"Monitoring folder: {MONITORED_PATH}", flush=True)
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