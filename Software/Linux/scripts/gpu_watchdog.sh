#!/bin/bash
#
# NeuralTower GPU Health Check
# Запускается до старта vLLM/SGLang. Проверяет наличие всех 4 GPU.
# Возвращает 0 если GPU=4, возвращает 1 и блокирует запуск если GPU<4.
#

EXPECTED_GPU_COUNT=4
LOG_FILE="/var/log/neural_tower_gpu_check.log"
MAX_RETRIES=5
RETRY_DELAY=30

log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [GPU-STARTUP-CHECK] $1" | tee -a "$LOG_FILE"
}

check_gpus() {
    local count
    count=$(nvidia-smi --query-gpu=index --format=csv,noheader,nounits 2>/dev/null | wc -l)
    echo "$count"
}

log_msg "=== NeuralTower GPU Startup Check ==="

attempt=0
while [ "$attempt" -lt "$MAX_RETRIES" ]; do
    gpu_count=$(check_gpus)
    attempt=$((attempt + 1))

    if [ "$gpu_count" -eq "$EXPECTED_GPU_COUNT" ]; then
        log_msg "OK: Все $EXPECTED_GPU_COUNT GPU обнаружены (попытка $attempt/$MAX_RETRIES)."
        log_msg "GPU list:"
        nvidia-smi --query-gpu=index,name,temperature.gpu,power.draw --format=csv | while IFS= read -r line; do
            log_msg "  $line"
        done
        exit 0
    fi

    log_msg "FAIL: Обнаружено GPU=$gpu_count из $EXPECTED_GPU_COUNT (попытка $attempt/$MAX_RETRIES)."

    if [ "$attempt" -lt "$MAX_RETRIES" ]; then
        log_msg "Ожидание ${RETRY_DELAY}s до повторной проверки..."
        sleep "$RETRY_DELAY"
    fi
done

log_msg "CRITICAL: Не обнаружены все 4 GPU после $MAX_RETRIES попыток."
log_msg "Система не будет запущена. Возможные причины:"
log_msg "  - Ведомый БП не запустился (проверить Add2PSU, LED-индикаторы)"
log_msg "  - Кабели питания мезонина 2 не подключены"
log_msg "  - Ошибка PCIe/PLX (проверить dmesg, nvidia-smi topo -m)"

nvidia-smi --query-gpu=index,name,temperature.gpu,power.draw --format=csv 2>&1 | while IFS= read -r line; do
    log_msg "  $line"
done

dmesg | grep -iE 'nvidia|pci|plx|error|fail' | tail -20 | while IFS= read -r line; do
    log_msg "dmesg: $line"
done

exit 1
