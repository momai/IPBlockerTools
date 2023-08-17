import re
from collections import Counter
from datetime import datetime, timedelta
from io import SEEK_END, SEEK_CUR
import json
import subprocess


# Чтение JSON-конфига
with open('config.json', 'r') as f:
    config = json.load(f)

ip_count = Counter()

# Шаблон регулярного выражения для IP-адресов и времени
ip_pattern = r'(?P<ip>\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b).*\[(?P<date>\d{2}\/\w{3}\/\d{4}:\d{2}:\d{2}:\d{2})'
ip_regex = re.compile(ip_pattern)

# Временной интервал для анализа (10 секунд)
time_interval = timedelta(seconds=config["time_interval_seconds"])

# Текущее время
now = datetime.utcnow()

def readlines_reverse(file):
    file.seek(0, SEEK_END)
    position = file.tell()
    line = ''
    while position >= 0:
        file.seek(position)
        next_char = file.read(1)
        if next_char == '\n':
            yield line[::-1]
            line = ''
        else:
            line += next_char
        position -= 1
    yield line[::-1]

# Обработка лог-файла с конца
#with open(config["file_path"], 'r') as file:
#    for line in readlines_reverse(file):
#        match = ip_regex.search(line)
#        if match:
#            log_time = datetime.strptime(match.group('date'), "%d/%b/%Y:%H:%M:%S")
#            if (now - log_time).total_seconds() <= time_interval.total_seconds():
#                ip_count.update([match.group('ip')])
#            else:
#                break

# Обработка лог-файла с конца
command = ["docker", "logs", "flomarket_nginx"]
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Получение всех строк вывода и их обращение
lines = process.stdout.readlines()
for line in reversed(lines):
    match = ip_regex.search(line)
    if match:
        log_time = datetime.strptime(match.group('date'), "%d/%b/%Y:%H:%M:%S")
        if (now - log_time).total_seconds() <= time_interval.total_seconds():
            ip_count.update([match.group('ip')])
        else:
            break


# Вывод результатов в консоль и в файл
with open(config["output_file_path"], 'w') as f:
    for ip, count in ip_count.most_common():
        if count > config["output_threshold_count"]:
            print(f'{ip} {count}')
            f.write(f'{ip} {count}\n')

# Выполнение скрипта на языке shell
subprocess.call(['/bin/bash', 'block_ips.sh'])
