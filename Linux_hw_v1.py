import subprocess

from collections import defaultdict
from datetime import datetime


def get_ps_aux_output():
    result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


def parse_ps_aux_output(output):
    lines = output.strip().split('\n')
    headers = lines[0].split()
    data = defaultdict(lambda: defaultdict(int))
    total_memory = 0.0
    total_cpu = 0.0
    max_memory_process = ('', 0.0)
    max_cpu_process = ('', 0.0)
    users = set()

    for line in lines[1:]:
        parts = line.split(None, len(headers) - 1)
        user = parts[0]
        cpu = float(parts[2])
        memory = float(parts[3])
        command = parts[-1]

        users.add(user)
        data[user]['processes'] += 1
        total_memory += memory
        total_cpu += cpu

        if memory > max_memory_process[1]:
            max_memory_process = (command, memory)
        if cpu > max_cpu_process[1]:
            max_cpu_process = (command, cpu)

    return {
        'users': users,
        'total_processes': sum(data[user]['processes'] for user in users),
        'user_processes': data,
        'total_memory': total_memory,
        'total_cpu': total_cpu,
        'max_memory_process': max_memory_process,
        'max_cpu_process': max_cpu_process
    }


def generate_report(data):
    report = "Отчёт о состоянии системы:\n"
    report += f"Пользователи системы: {', '.join(sorted(data['users']))}\n"
    report += f"Процессов запущено: {data['total_processes']}\n\n"

    report += "Пользовательских процессов:\n"
    for user, stats in sorted(data['user_processes'].items()):
        report += f"{user}: {stats['processes']}\n"

    report += f"\nВсего памяти используется: {data['total_memory']:.1f}%\n"
    report += f"Всего CPU используется: {data['total_cpu']:.1f}%\n"

    max_memory_process, max_memory_usage = data['max_memory_process']
    max_cpu_process, max_cpu_usage = data['max_cpu_process']

    report += f"Больше всего памяти использует: {max_memory_process[:20]} ({max_memory_usage:.1f}%)\n"
    report += f"Больше всего CPU использует: {max_cpu_process[:20]} ({max_cpu_usage:.1f}%)\n"

    return report


def save_report_to_file(report):
    timestamp = datetime.now().strftime("%d-%m-%Y-%H:%M-scan.txt")
    with open(timestamp, 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    output = get_ps_aux_output()
    data = parse_ps_aux_output(output)
    report = generate_report(data)
    print(report)
    save_report_to_file(report)


if __name__ == "__main__":
    main()
