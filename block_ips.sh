#!/bin/bash
source .env

function get_abuse_ipdb_info() {
    local ip_address="$1"
    local api_key=$ABUSEIPDB_API
    local whois_info=$(whois "$ip_address")
    local route=$(echo "$whois_info" | grep -E 'route:')
    local abuse_info=$(curl -s -G https://api.abuseipdb.com/api/v2/check \
        --data-urlencode "ipAddress=$ip_address" \
        -d maxAgeInDays=90 \
        -d verbose \
        -H "Key: $api_key" \
        -H "Accept: application/json" | jq -r '.data')

    echo "Whois информация:"
    echo "$whois_info"
    echo ""
    echo "AbuseIPDB информация:"
    echo "$abuse_info"
    echo ""

    if [ ! -z "$route" ]; then
        echo "Подсеть:"
        echo "$route"
        echo ""
    fi

    return 0
}

# Создайте цепочку BLOCKED_IPS, если она еще не существует
sudo iptables -N BLOCKED_IPS 2>/dev/null || true

# Прочитайте список IP-адресов из файла blocked_ips.txt и блокируйте их в iptables
while read -r line; do
    IP_ADDRESS=$(echo "$line" | awk '{print $1}')
    duplicate_count=$(echo "$line" | awk '{print $2}')

    echo "Информация для IP-адреса $IP_ADDRESS (дублей: $duplicate_count):"
    get_abuse_ipdb_info "$IP_ADDRESS"
    route=$(whois "$IP_ADDRESS" | grep -E 'route:')

    if [ ! -z "$route" ]; then
        read -p "Вы хотите заблокировать всю подсеть $route (дублей: $duplicate_count)? (y/n) " subnet_answer </dev/tty
        if [ "$subnet_answer" == "y" ]; then
            sudo iptables -A BLOCKED_IPS -s "$(echo "$route" | awk '{print $2}')" -j DROP
            echo "Заблокирована подсеть $route"
            continue
        fi
    fi

    read -p "Вы хотите заблокировать IP-адрес $IP_ADDRESS (дублей: $duplicate_count)? (y/n) " answer </dev/tty

    if [ "$answer" == "y" ]; then
        sudo iptables -A BLOCKED_IPS -s "$IP_ADDRESS" -j DROP
        echo "Заблокирован IP-адрес $IP_ADDRESS"
    else
        echo "Пропуск IP-адреса $IP_ADDRESS"
    fi
done < $output_file_path

# Примените цепочку BLOCKED_IPS к INPUT, если она еще не применена
sudo iptables -C INPUT -j BLOCKED_IPS 2>/dev/null || sudo iptables -A INPUT -j BLOCKED_IPS
