#!/bin/bash

# Скрипт мониторинга состояния NeuralTower V-Core
# Выводит статус 4-х GPU Tesla V100 и системные параметры

clear
echo "=== NeuralTower System Monitor ==="
echo "Press Ctrl+C to exit"
echo "----------------------------------"

while true; do
    # Сбор данных через nvidia-smi
    # Выводим: Индекс, Название, Температуру, Нагрузку, Память и Потребление
    nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw --format=csv,noheader,nounits | awk -F', ' '{
        printf "GPU [%s] %-10s | Temp: %3s°C | Load: %3s%% | VRAM: %5s/%s MB | Power: %sW\n", $1, $2, $3, $4, $5, $6, $7
    }'

    echo "----------------------------------"
    
    # Мониторинг процессора и NVMe Swap (для контроля работы vLLM)
    CPU_TEMP=$(sensors | grep "Package id 0" | awk '{print $4}')
    SWAP_USAGE=$(free -m | grep "Swap" | awk '{print $3}')
    
    echo "CPU Temp: $CPU_TEMP"
    echo "NVMe Swap Usage: ${SWAP_USAGE}MB"
    
    # Рекомендация по безопасности
    GPU_MAX_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits | sort -nr | head -1)
    if [ "$GPU_MAX_TEMP" -gt 65 ]; then
        echo -e "\033[0;31mWARNING: High Temperature Detected! Check V-Core Pressure!\033[0m"
    fi

    sleep 2
    # Возвращаемся в начало вывода для эффекта живого обновления
    echo -e "\033[12A" 
done
