from collections import Counter, defaultdict


SUSPICIOUS_USER_AGENTS = [
    "curl",
    "python-requests",
    "sqlmap",
    "nikto",
    "nmap",
]


SUSPICIOUS_PATH_PATTERNS = [
    "../",
    "/etc/passwd",
    "wp-admin",
    "phpmyadmin",
    ".env",
]


def detect_brute_force(events, threshold=3):
    findings = []
    failed_auth_by_ip = defaultdict(list)

    for event in events:
        if event["status"] in [401, 403]:
            failed_auth_by_ip[event["ip"]].append(event)

    for ip, failed_events in failed_auth_by_ip.items():
        if len(failed_events) >= threshold:
            findings.append({
                "severity": "HIGH",
                "type": "POSSIBLE_BRUTE_FORCE",
                "ip": ip,
                "count": len(failed_events),
                "description": "Multiple failed authentication attempts from the same IP address.",
            })

    return findings


def detect_scanning(events, threshold=3):
    findings = []
    not_found_by_ip = defaultdict(list)

    for event in events:
        if event["status"] == 404:
            not_found_by_ip[event["ip"]].append(event)

    for ip, not_found_events in not_found_by_ip.items():
        if len(not_found_events) >= threshold:
            findings.append({
                "severity": "MEDIUM",
                "type": "POSSIBLE_WEB_SCANNING",
                "ip": ip,
                "count": len(not_found_events),
                "description": "Multiple 404 responses from the same IP address.",
            })

    return findings


def detect_directory_traversal(events):
    findings = []

    for event in events:
        path = event["path"].lower()

        if "../" in path or "/etc/passwd" in path:
            findings.append({
                "severity": "HIGH",
                "type": "DIRECTORY_TRAVERSAL_ATTEMPT",
                "ip": event["ip"],
                "path": event["path"],
                "status": event["status"],
                "description": "Request path contains directory traversal indicators.",
            })

    return findings


def detect_suspicious_user_agents(events):
    findings = []

    for event in events:
        user_agent = event["user_agent"].lower()

        for suspicious_agent in SUSPICIOUS_USER_AGENTS:
            if suspicious_agent in user_agent:
                findings.append({
                    "severity": "LOW",
                    "type": "SUSPICIOUS_USER_AGENT",
                    "ip": event["ip"],
                    "user_agent": event["user_agent"],
                    "path": event["path"],
                    "description": "Request used a suspicious or automated user agent.",
                })
                break

    return findings


def detect_suspicious_paths(events):
    findings = []

    for event in events:
        path = event["path"].lower()

        for pattern in SUSPICIOUS_PATH_PATTERNS:
            if pattern in path:
                findings.append({
                    "severity": "MEDIUM",
                    "type": "SUSPICIOUS_PATH_REQUEST",
                    "ip": event["ip"],
                    "path": event["path"],
                    "status": event["status"],
                    "matched_pattern": pattern,
                    "description": "Request path matched a suspicious pattern.",
                })
                break

    return findings


def run_detections(events):
    findings = []

    findings.extend(detect_brute_force(events))
    findings.extend(detect_scanning(events))
    findings.extend(detect_directory_traversal(events))
    findings.extend(detect_suspicious_user_agents(events))
    findings.extend(detect_suspicious_paths(events))

    return findings