#to use it: python kurochkin/Downloads/PycharmProjects/linux_hw_v2.py kurochkin/Downloads/access.log

import os
import re
import json
import argparse
from collections import defaultdict, Counter

log_pattern = re.compile(
    r'(?P<ip>[\d.]+) - - \[(?P<time>[^\]]+)] "(?P<method>[A-Z]+) (?P<url>[^"]+) HTTP/\d\.\d" (?P<status>\d{3}) (?P<size>\d+|-) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)" (?P<duration>\d+)')


def parse_log_line(line):
    match = log_pattern.match(line)
    if match:
        return match.groupdict()
    return None


def analyze_log_file(file_path):
    total_requests = 0
    method_counter = Counter()
    ip_counter = Counter()
    longest_requests = []

    with open(file_path, 'r') as file:
        for line in file:
            log_data = parse_log_line(line)
            if log_data:
                total_requests += 1
                method_counter[log_data['method']] += 1
                ip_counter[log_data['ip']] += 1
                request_info = {
                    'method': log_data['method'],
                    'url': log_data['url'],
                    'ip': log_data['ip'],
                    'duration': int(log_data['duration']),
                    'time': log_data['time']
                }
                longest_requests.append(request_info)

    longest_requests = sorted(longest_requests, key=lambda x: x['duration'], reverse=True)[:3]

    result = {
        'total_requests': total_requests,
        'method_count': method_counter,
        'top_3_ips': ip_counter.most_common(3),
        'top_3_longest_requests': longest_requests
    }
    return result


def process_logs(log_dir_or_file):
    if os.path.isfile(log_dir_or_file):
        files_to_process = [log_dir_or_file]
    elif os.path.isdir(log_dir_or_file):
        files_to_process = [os.path.join(log_dir_or_file, f) for f in os.listdir(log_dir_or_file) if
                            os.path.isfile(os.path.join(log_dir_or_file, f))]
    else:
        raise ValueError(f"{log_dir_or_file} is not a valid file or directory")

    for file_path in files_to_process:
        print(f"Processing file: {file_path}")
        stats = analyze_log_file(file_path)

        output_file = f"{file_path}_stats.json"
        with open(output_file, 'w') as json_file:
            json.dump(stats, json_file, indent=4)

        print(json.dumps(stats, indent=4))


def main():
    parser = argparse.ArgumentParser(description="Анализатор лог-файлов access.log")
    parser.add_argument('log_dir_or_file', help="Директория с логами или конкретный файл")
    args = parser.parse_args()

    process_logs(args.log_dir_or_file)


if __name__ == "__main__":
    main()
