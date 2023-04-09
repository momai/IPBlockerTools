#!/bin/bash

# Создайте цепочку BLOCKED_IPS, если она еще не существует
sudo iptables -N BLOCKED_IPS 2>/dev/null || true

# Прочитайте список IP-адресов из файла blocked_ips.txt и блокируйте их в iptables
while read -r line; do
    IP_ADDRESS=$(echo "$line" | awk '{print $1}')
    duplicate_count=$(echo "$line" | awk '{print $2}')

    read -p "Вы хотите заблокировать IP-адрес $IP_ADDRESS (дублей: $duplicate_count)? (y/n) " answer </dev/tty

    if [ "$answer" == "y" ]; then
        sudo iptables -A BLOCKED_IPS -s "$IP_ADDRESS" -j DROP
        echo "Заблокирован IP-адрес $IP_ADDRESS"
    else
        echo "Пропуск IP-адреса $IP_ADDRESS"
    fi
done < blocked_ips.txt

# Примените цепочку BLOCKED_IPS к INPUT, если она еще не применена
sudo iptables -C INPUT -j BLOCKED_IPS 2>/dev/null || sudo iptables -A INPUT -j BLOCKED_IPS
