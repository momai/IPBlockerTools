import re
from collections import Counter
from datetime import datetime, timedelta
from io import SEEK_END, SEEK_CUR

ip_count = Counter()

# Шаблон регулярного выражения для IP-адресов и времени
ip_pattern = r'(?P<ip>\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b).*\[(?P<date>\d{2}\/\w{3}\/\d{4}:\d{2}:\d{2}:\d{2})'
ip_regex = re.compile(ip_pattern)

# Временной интервал для анализа (10 секунд)
time_interval = timedelta(seconds=10)

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
with open('nginx/forumhouse.ru.access.log', 'r') as file:
    for line in readlines_reverse(file):
        match = ip_regex.search(line)
        if match:
            log_time = datetime.strptime(match.group('date'), "%d/%b/%Y:%H:%M:%S")
            if (now - log_time).total_seconds() <= time_interval.total_seconds():
                ip_count.update([match.group('ip')])
            else:
                break

# Вывод результатов в консоль
for ip, count in ip_count.most_common():
    print(f'{ip} {count}')

# Сохраняем результаты в файл
#with open('blocked_ips.txt', 'w') as f:
#    for ip, count in ip_count.most_common():
#        f.write(f'{ip}\n')

# Сохраняем результаты в файл
with open('blocked_ips.txt', 'w') as f:
    for ip, count in ip_count.most_common():
        f.write(f'{ip} {count}\n')
