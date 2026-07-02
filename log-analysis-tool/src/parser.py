import re


APACHE_LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>.*?)\] '
    r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>.*?)" '
    r'(?P<status>\d{3}) (?P<size>\S+) '
    r'"(?P<referrer>.*?)" "(?P<user_agent>.*?)"'
)


def parse_apache_line(line):
    match = APACHE_LOG_PATTERN.match(line)

    if not match:
        return None

    data = match.groupdict()
    data["status"] = int(data["status"])

    return data


def parse_log_file(file_path):
    events = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parsed = parse_apache_line(line.strip())

            if parsed:
                events.append(parsed)

    return events