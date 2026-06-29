from baseline import load_baseline, calculate_sha256
import os


def check_integrity(monitored_path, baseline_file):
    baseline = load_baseline(baseline_file)
    results = []

    current_files = {}

    for root, _, files in os.walk(monitored_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            current_files[file_path] = calculate_sha256(file_path)

    for path, expected_hash in baseline.items():
        if path not in current_files:
            results.append({
                "path": path,
                "status": "FILE_DELETED",
                "severity": "CRITICAL",
                "expected_sha256": expected_hash,
                "actual_sha256": None,
            })
        elif current_files[path] != expected_hash:
            results.append({
                "path": path,
                "status": "BASELINE_MISMATCH",
                "severity": "CRITICAL",
                "expected_sha256": expected_hash,
                "actual_sha256": current_files[path],
            })
        else:
            results.append({
                "path": path,
                "status": "MATCHES_BASELINE",
                "severity": "INFO",
                "expected_sha256": expected_hash,
                "actual_sha256": current_files[path],
            })

    for path, actual_hash in current_files.items():
        if path not in baseline:
            results.append({
                "path": path,
                "status": "NEW_FILE_NOT_IN_BASELINE",
                "severity": "WARNING",
                "expected_sha256": None,
                "actual_sha256": actual_hash,
            })

    return results