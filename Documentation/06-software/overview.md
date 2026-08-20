# Обзор программного стека

## Маршрут от включения до инференса

Программный стек NeuralTower следует детерминированному пути от инициализации железа до инференса модели:

1. **Настройка BIOS** — Above 4G Decoding, принудительный PCIe Gen3, UEFI-режим (см. [bios-settings.md](../05-hardware/bios-settings.md))
2. **Linux и драйверы** — Gentoo с параметрами ядра `pci=realloc,assign-busses pci=hp_pcie_bus_max`, NVIDIA-драйвер с `uvm`, все 4 GPU видны (см. [system-setup.md](./system-setup.md))
3. **Оптимизация Gentoo** — компиляция под Broadwell, hugepages, настройка NUMA (см. [gentoo-config.md](./gentoo-config.md))
4. **Сборка ML-окружения** — CUDA 12.8, Python 3.12, PyTorch cu128, установка vLLM/SGLang (см. [world-build.md](./world-build.md))
5. **Движок инференса** — 1Cat-vLLM или SGLang с топологией TP=2 + PP=2 (см. [vllm.md](./vllm.md) или [sglang/README.md](./sglang/README.md))
6. **Мониторинг** — панель Grafana + GPU Watchdog (см. [monitoring.md](./monitoring.md))

## Пути выбора движка инференса

### Путь A: 1Cat-vLLM (рекомендуемый)

Форк с восстановленной поддержкой V100, FlashAttention-2 для sm_70 и квантизацией AWQ 4-bit. Готовые wheel-пакеты для CUDA 12.8 + Python 3.12.

### Путь B: официальный vLLM 0.18.x (альтернатива)

Последний официальный релиз с нативной поддержкой sm_70. Использует Triton JIT-ядра. Медленнее FlashAttention-2, но стабилен.

> Официальный vLLM 0.20+ полностью убрал поддержку sm_70 (CUDA 13.0, PyTorch 2.11+). На V100 не работает.

### Путь C: SGLang (альтернатива)

Трёхуровневый HiCache (GPU HBM → CPU RAM → NVMe SSD), повторное использование контекста RadixAttention, спекулятивное декодирование EAGLE/MTP. См. [sglang/README.md](./sglang/README.md).

## Ключевые ограничения

| Ограничение | Значение | Причина |
|-----------|-------|--------|
| Архитектура GPU | V100 sm_70 | Архитектура Volta, 2017 год |
| Версия CUDA | 12.8 | Последняя стабильная версия с полной поддержкой sm_70 |
| Точность | Только FP16 | BF16 эмулируется (медленно), FP8/MXFP4 недоступны (нужен sm_80+) |
| Python | 3.12 | Требуется для готовых wheel-пакетов 1Cat-vLLM |
| Память GPU | 32 ГБ на GPU (128 ГБ суммарно) | V100 SXM2-32G |

## Профили ядра

Система поддерживает два профиля ядра, выбираемых при загрузке через GRUB:

- **Performance** — максимальная пропускная способность KV-кэша, без защитных mitigations
- **Hardened** — KASLR, защита стека, lockdown-режим

Инструкции по сборке — в [profiles.md](./profiles.md).

## Связанные документы

| Файл | Описание |
|------|-------------|
| [system-setup.md](./system-setup.md) | Маршрут от включения до первого запуска модели |
| [gentoo-config.md](./gentoo-config.md) | Оптимизация Gentoo для vLLM и SGLang |
| [world-build.md](./world-build.md) | Воспроизводимая установка Python/CUDA/PyTorch/vLLM |
| [vllm.md](./vllm.md) | Оптимизация vLLM, TP/PP, NCCL, NVMe swap |
| [sglang/README.md](./sglang/README.md) | Развёртывание SGLang с Prometheus/Grafana |
| [monitoring.md](./monitoring.md) | Панель Grafana и GPU Watchdog |
| [profiles.md](./profiles.md) | Профили ядра Performance и Hardened |
