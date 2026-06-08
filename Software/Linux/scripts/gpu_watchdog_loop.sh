#!/bin/bash
#
# NeuralTower GPU Watchdog
# Фоновый демон. Постоянно проверяет наличие всех 4 GPU.
# При потере любого GPU: логирование + graceful shutdown workload-контейнеров.
#

EXPECTED_GPU_COUNT=4
CHECK_INTERVAL=10
LOG_FILE="/var/log/neural_tower_gpu_watchdog.log"
SHUTDOWN_DONE_MARKER="/tmp/neural_tower_watchdog_shutdown_done"
VLLM_CONTAINER="neural_tower_vllm"
SGLANG_CONTAINER="sglang_core_server"

log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [GPU-WATCHDOG] $1" | tee -a "$LOG_FILE"
}

check_gpus() {
    local count
    count=$(nvidia-smi --query-gpu=index --format=csv,noheader,nounits 2>/dev/null | wc -l)
    echo "$count"
}

shutdown_workloads() {
    log_msg "=== EMERGENCY SHUTDOWN ==="

    if [ -f "$SHUTDOWN_DONE_MARKER" ]; then
        log_msg "Shutdown уже инициирован ранее. Пропуск."
        return
    fi

    touch "$SHUTDOWN_DONE_MARKER"

    log_msg "Остановка workload-контейнеров..."

    docker stop "$VLLM_CONTAINER" 2>/dev/null
    log_msg "Контейнер $VLLM_CONTAINER остановлен (exit: $?)."

    docker stop "$SGLANG_CONTAINER" 2>/dev/null
    log_msg "Контейнер $SGLANG_CONTAINER остановлен (exit: $?)."

    nvidia-smi --query-gpu=index,name,power.draw,temperature.gpu --format=csv 2>&1 | while IFS= read -r line; do
        log_msg "GPU state: $line"
    done

    dmesg | tail -30 | while IFS= read -r line; do
        log_msg "dmesg: $line"
    done

    log_msg "=== SHUTDOWN COMPLETE ==="
    log_msg "Требуется диагностика и перезагрузка системы."
}

log_msg "=== NeuralTower GPU Watchdog Started ==="
log_msg "Ожидается GPU=$EXPECTED_GPU_COUNT, интервал проверки=${CHECK_INTERVAL}s"

while true; do
    gpu_count=$(check_gpus)

    if [ "$gpu_count" -lt "$EXPECTED_GPU_COUNT" ]; then
        log_msg "CRITICAL: Потеря GPU! Текущее количество=$gpu_count, ожидалось=$EXPECTED_GPU_COUNT"

        remaining_gpus=$(nvidia-smi --query-gpu=index,name --format=csv,noheader 2>/dev/null)
        log_msg "Оставшиеся GPU:"
        echo "$remaining_gpus" | while IFS= read -r line; do
            log_msg "  $line"
        done

        missing_indices=$(nvidia-smi --query-gpu=index --format=csv,noheader,nounits 2>/dev/null | sort -n)
        for i in $(seq 0 $((EXPECTED_GPU_COUNT - 1))); do
            if ! echo "$missing_indices" | grep -q "^${i}$"; then
                log_msg "  GPU $i — НЕ ДОСТУПЕН"
            fi
        done

        shutdown_workloads
    else
        if [ "$gpu_count" -gt "$EXPECTED_GPU_COUNT" ]; then
            log_msg "WARNING: Обнаружено GPU=$gpu_count (ожидалось $EXPECTED_GPU_COUNT). Возможна смена конфигурации."
        fi
    fi

    sleep "$CHECK_INTERVAL"
done
