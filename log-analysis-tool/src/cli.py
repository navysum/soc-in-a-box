from parser import parse_log_file
from analyzer import summarize_events
from detector import run_detections
import argparse
import json
import os


REPORT_PATH = "reports/summary.json"


def main():
    parser = argparse.ArgumentParser(description="Log Analysis Tool")
    parser.add_argument("--file", required=True, help="Path to the log file")

    args = parser.parse_args()

    events = parse_log_file(args.file)
    summary = summarize_events(events)
    detections = run_detections(events)

    report_data = {
        "summary": summary,
        "detections": detections,
    }

    os.makedirs("reports", exist_ok=True)

    with open(REPORT_PATH, "w", encoding="utf-8") as report:
        json.dump(report_data, report, indent=4)

    print(json.dumps(report_data, indent=4), flush=True)
    print(f"Report saved to: {REPORT_PATH}", flush=True)


if __name__ == "__main__":
    main()