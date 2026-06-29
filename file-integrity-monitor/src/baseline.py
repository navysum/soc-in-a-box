import hashlib
import json
import os


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for block in iter(lambda: file.read(4096), b""):
            sha256.update(block)

    return sha256.hexdigest()


def build_baseline(monitored_path):
    baseline = {}

    for root, _, files in os.walk(monitored_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            baseline[file_path] = calculate_sha256(file_path)

    return baseline


def save_baseline(baseline, baseline_file):
    os.makedirs(os.path.dirname(baseline_file), exist_ok=True)

    with open(baseline_file, "w", encoding="utf-8") as file:
        json.dump(baseline, file, indent=4)


def load_baseline(baseline_file):
    if not os.path.exists(baseline_file):
        return {}

    with open(baseline_file, "r", encoding="utf-8") as file:
        return json.load(file)