from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class FileChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"[CREATED] {event.src_path}")

    def on_modified(self, event):
        print(f"[MODIFIED] {event.src_path}")

    def on_deleted(self, event):
        print(f"[DELETED] {event.src_path}")

if __name__ == "__main__":
    path = "monitored"

    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    print(f"Monitoring folder: {path}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()