from parser import parse_log_file
from analyzer import summarize_events
from detector import run_detections
from reporter import generate_markdown_report
import argparse
import json
import os


JSON_REPORT_PATH = "reports/summary.json"
MARKDOWN_REPORT_PATH = "reports/summary.md"


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

    with open(JSON_REPORT_PATH, "w", encoding="utf-8") as report:
        json.dump(report_data, report, indent=4)

    markdown_report = generate_markdown_report(report_data, MARKDOWN_REPORT_PATH)

    print(json.dumps(report_data, indent=4), flush=True)
    print(f"JSON report saved to: {JSON_REPORT_PATH}", flush=True)
    print(f"Markdown report saved to: {markdown_report}", flush=True)


if __name__ == "__main__":
    main()