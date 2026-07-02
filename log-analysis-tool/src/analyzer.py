from collections import Counter


def summarize_events(events):
    total_requests = len(events)
    status_codes = Counter(event["status"] for event in events)
    top_ips = Counter(event["ip"] for event in events)

    return {
        "total_requests": total_requests,
        "status_codes": dict(status_codes),
        "top_ips": dict(top_ips.most_common(5)),
    }