from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from baseline import build_baseline, save_baseline, load_baseline, calculate_sha256
from checker import check_integrity
from report import generate_summary_report
from datetime import datetime
import argparse
import json
import time
import os


MONITORED_PATH = os.getenv("MONITORED_PATH", "monitored")
REPORTS_PATH = os.getenv("REPORTS_PATH", "reports")
EVENT_LOG_FILE = os.path.join(REPORTS_PATH, "events.jsonl")
BASELINE_FILE = os.path.join(REPORTS_PATH, "baseline.json")
SUMMARY_REPORT_FILE = os.path.join(REPORTS_PATH, "summary.md")


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_severity(event_type, integrity_status=None):
    if integrity_status in ["BASELINE_MISMATCH", "FILE_DELETED"]:
        return "CRITICAL"
    if integrity_status == "NEW_FILE_NOT_IN_BASELINE":
        return "WARNING"
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

        try:
            file_hash = calculate_sha256(path)
        except FileNotFoundError:
            file_hash = None
        except PermissionError:
            file_hash = "PERMISSION_DENIED"

        baseline = load_baseline(BASELINE_FILE)
        expected_hash = baseline.get(path)

        if event_type == "DELETED":
            integrity_status = "FILE_DELETED"
        elif expected_hash is None:
            integrity_status = "NEW_FILE_NOT_IN_BASELINE"
        elif expected_hash == file_hash:
            integrity_status = "MATCHES_BASELINE"
        else:
            integrity_status = "BASELINE_MISMATCH"

        severity = get_severity(event_type, integrity_status)

        event_data = {
            "timestamp": timestamp,
            "event_type": event_type,
            "severity": severity,
            "integrity_status": integrity_status,
            "path": path,
            "destination": destination,
            "expected_sha256": expected_hash,
            "actual_sha256": file_hash,
        }

        save_event(event_data)

        message = f"[{timestamp}] [{severity}] [{event_type}] {path} [{integrity_status}]"

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
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current files against the trusted baseline",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate a Markdown integrity summary report",
    )

    args = parser.parse_args()

    os.makedirs(MONITORED_PATH, exist_ok=True)
    os.makedirs(REPORTS_PATH, exist_ok=True)

    if args.init_baseline:
        baseline = build_baseline(MONITORED_PATH)
        save_baseline(baseline, BASELINE_FILE)
        print(f"Baseline saved to: {BASELINE_FILE}", flush=True)
        return

    if args.check:
        results = check_integrity(MONITORED_PATH, BASELINE_FILE)

        for result in results:
            print(
                f"[{result['severity']}] "
                f"{result['status']} "
                f"{result['path']}",
                flush=True,
            )

        return

    if args.report:
        report_file = generate_summary_report(
            MONITORED_PATH,
            BASELINE_FILE,
            SUMMARY_REPORT_FILE,
        )
        print(f"Summary report generated: {report_file}", flush=True)
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