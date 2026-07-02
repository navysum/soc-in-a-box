import os


def generate_markdown_report(report_data, output_path="reports/summary.md"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    summary = report_data["summary"]
    detections = report_data["detections"]

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("# Log Analysis Report\n\n")

        file.write("## Summary\n\n")
        file.write(f"- Total Requests: {summary['total_requests']}\n")
        file.write(f"- Total Detections: {len(detections)}\n\n")

        file.write("## Status Codes\n\n")
        file.write("| Status Code | Count |\n")
        file.write("|---|---|\n")

        for status, count in summary["status_codes"].items():
            file.write(f"| {status} | {count} |\n")

        file.write("\n## Top IPs\n\n")
        file.write("| IP Address | Requests |\n")
        file.write("|---|---|\n")

        for ip, count in summary["top_ips"].items():
            file.write(f"| {ip} | {count} |\n")

        file.write("\n## Detections\n\n")
        file.write("| Severity | Type | IP | Description |\n")
        file.write("|---|---|---|---|\n")

        for detection in detections:
            file.write(
                f"| {detection['severity']} | "
                f"{detection['type']} | "
                f"{detection.get('ip', 'N/A')} | "
                f"{detection['description']} |\n"
            )

    return output_path