from checker import check_integrity
from datetime import datetime
import os


def generate_summary_report(monitored_path, baseline_file, report_file):
    results = check_integrity(monitored_path, baseline_file)

    os.makedirs(os.path.dirname(report_file), exist_ok=True)

    critical = [r for r in results if r["severity"] == "CRITICAL"]
    warning = [r for r in results if r["severity"] == "WARNING"]
    info = [r for r in results if r["severity"] == "INFO"]

    with open(report_file, "w", encoding="utf-8") as file:
        file.write("# File Integrity Summary Report\n\n")
        file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        file.write("## Summary\n\n")
        file.write(f"- Critical: {len(critical)}\n")
        file.write(f"- Warning: {len(warning)}\n")
        file.write(f"- Info: {len(info)}\n\n")

        file.write("## Results\n\n")
        file.write("| Severity | Status | Path |\n")
        file.write("|---|---|---|\n")

        for result in results:
            file.write(
                f"| {result['severity']} | {result['status']} | {result['path']} |\n"
            )

    return report_file