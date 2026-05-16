# Используем официальный базовый образ Ubuntu с поддержкой CUDA 12.4
FROM nvidia/cuda:12.4.1-base-ubuntu22.04

# Отключаем интерактивные диалоги при установке пакетов
ENV DEBIAN_FRONTEND=noninteractive

# Устанавливаем базовые зависимости для добавления репозиториев
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Добавляем официальный репозиторий NVIDIA DCGM для Ubuntu 22.04
RUN curl -fsSL https://nvidia.com | gpg --dearmor -o /usr/share/keyrings/nvidia-drivers.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/nvidia-drivers.gpg] https://nvidia.com /" > /etc/apt/sources.list.d/nvidia-gputools.list

# Устанавливаем пакет Data Center GPU Manager (DCGM)
RUN apt-get update && apt-get install -y --no-install-recommends \
    datacenter-gpu-manager \
    && rm -rf /var/lib/apt/lists/*

# Копируем скрипт автоматической диагностики внутрь контейнера
COPY run_diagnostic.sh /usr/local/bin/run_diagnostic.sh
RUN chmod +x /usr/local/bin/run_diagnostic.sh

# Точка входа для запуска автоматического скрипта проверки
ENTRYPOINT ["/usr/local/bin/run_diagnostic.sh"]
