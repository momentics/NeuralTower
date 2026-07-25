# Развёртывание SGLang

Готовое решение для сервера SGLang с мониторингом Prometheus и панелями Grafana.

## Требования

- Docker Engine 20.10+
- Docker Compose 2.0+
- Ускорители NVIDIA с поддержкой CUDA
- Минимум 2 GPU для тензорного и конвейерного параллелизма

## Быстрый старт

1. Скопируйте `.env.example` в `.env` и настройте:
    ```bash
    cp .env.example .env
    # Измените значения по необходимости
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
| `MODELS_PATH` | `/opt/llm/models` | Путь к хранилищу моделей на хосте |
| `KV_CACHE_PATH` | `/nvme/sglang_kv_cache` | Путь к NVMe для HiCache L3 |
| `CUDA_VISIBLE_DEVICES` | `0,1,2,3` | Устройства GPU |
| `TP_SIZE` | `2` | Размер тензорного параллелизма |
| `PP_SIZE` | `2` | Размер конвейерного параллелизма |
| `MODEL_PATH` | `/models/Qwen3.6-27B-Instruct` | Путь к целевой модели |
| `EAGLE_DRAFT_MODEL_PATH` | `/models/EAGLE-Qwen3.6-27B-Instruct` | Модель-черновик EAGLE (не требуется для MTP-моделей) |
| `MEM_FRACTION_STATIC` | `0.50` | Доля памяти для весов и KV-кэша |
| `CUDA_GRAPH_MAX_BS` | `4` | Максимальный размер пакета CUDA-графа |
| `HICACHE_SIZE_GB` | `30` | Объём HiCache L2 в оперативной памяти на ранг (итого = значение × число рангов) |
| `SPECULATIVE_ALGO` | `EAGLE` | Алгоритм: `EAGLE`, `MTP` или `NGRAM` |
| `SPECULATIVE_NUM_STEPS` | `3` | Количество шагов спекуляции |
| `SPECULATIVE_EAGLE_TOPK` | `1` | Top-K для EAGLE |
| `SPECULATIVE_NUM_DRAFT_TOKENS` | `4` | Количество токенов-черновиков |

## Ограничения V100 (sm_70)

| Параметр | Значение | Причина |
|---------|-------|--------|
| `--dtype` | `float16` | V100 не поддерживает BF16 на аппаратном уровне |
| `--kv-cache-dtype` | `int8` | V100 поддерживает INT8 Tensor Cores |
| `--attention-backend` | `triton` | FlashInfer требует SM80+ |
| FP8 | Недоступен | V100 не имеет аппаратной поддержки FP8 |
| CUDA-графы + MTP | Размер захвата графа кратен `num_speculative_tokens + 1` | В противном случае возникает ошибка памяти |

## Варианты спекулятивного декодирования

### EAGLE (используется по умолчанию)

Использует внешнюю модель-черновик для предсказания токенов. Настроено в docker-compose.yml.

### MTP (Multi-Token Prediction)

MTP — архитектурная особенность модели, не зависит от аппаратного обеспечения. Работает на V100 (sm_70) как обычные операции GEMM. Модели семейства Qwen3.6 с MTP (например Qwen3.6-30B-A3B) имеют встроенные MTP-головы для параллельного предсказания нескольких токенов.

Для включения MTP:
- Установите `MODEL_PATH` на MTP-модель (например `/models/Qwen3.6-30B-A3B`)
- Удалите `--speculative-draft-model-path` из команды (MTP-головы встроены в модель)
- Используйте: `--speculative-num-steps 1 --speculative-eagle-topk 1 --speculative-num-draft-tokens 2`
- Установите `--cuda-graph-max-bs` кратным `num_speculative_tokens + 1` (например 4 при 2 токенах-черновиках)

### NGRAM

Модель-черновик не требуется. Используйте `--speculative-algorithm NGRAM` для спекуляции на основе n-грамм.

## Сервисы

- **sglang-server**: сервер инференса LLM со спекулятивным декодированием
- **prometheus**: сбор метрик
- **grafana**: панели мониторинга

## Примечания по безопасности

- Измените пароли перед использованием в производственной среде
- Ограничьте доступ к портам
- Монтируйте хранилище моделей только для чтения
