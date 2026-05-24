# Развертывание SGLang Production

Готовое решение для работы SGLang сервера с мониторингом Prometheus и Grafana дашбордами.

## Требования

- Docker Engine 20.10+
- Docker Compose 2.0+
- NVIDIA GPU(s) с поддержкой CUDA
- Минимум 2 GPU для тензорного/пайплайн параллелизма

## Быстрый старт

1. Скопируйте `.env.example` в `.env` и настройте:
   ```bash
   cp .env.example .env
   # Отредактируйте значения по необходимости
   ```

2. Создайте директорию кэша:
   ```bash
   chmod +x init-cache.sh
   ./init-cache.sh
   ```

3. Запустите сервисы:
   ```bash
   docker compose up -d
   ```

4. Откройте сервисы:
   - SGLang API: http://localhost:8000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin / ваш пароль из .env)

## Конфигурация

| Переменная | По умолчанию | Описание |
|----------|---------|-------------|
| `MODELS_PATH` | `/opt/llm/models` | Путь к моделям на хосте |
| `KV_CACHE_PATH` | `/mnt/optane_u2/sglang_kv_cache` | Путь к HiCache |
| `CUDA_VISIBLE_DEVICES` | `0,1,2,3` | GPU устройства |
| `TP_SIZE` | `2` | Размер тензорного параллелизма |
| `PP_SIZE` | `2` | Размер пайплайн параллелизма |
| `MEM_FRACTION_FAST` | `0.50` | Доля памяти для быстрой модели |
| `MEM_FRACTION_HEAVY` | `0.40` | Доля памяти для тяжелой модели |
| `HICACHE_CPU_MEMORY_LIMIT_GB` | `48` | Ограничение памяти HiCache |

## Сервисы

- **sglang-server**: Сервер инференса LLM с спекулятивным декодированием
- **prometheus**: Сбор метрик
- **grafana**: Дашборды мониторинга

## Примечания по безопасности

- Смените пароли перед использованием в продакшене
- Ограничьте доступ к портам
- Монтируйте хранилище моделей только для чтения