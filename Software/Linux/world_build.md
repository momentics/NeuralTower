# Полная сборка окружения NeuralTower

Данная инструкция описывает процесс развертывания, включая базовую настройку и оптимизацию Gentoo, конфигурацию компиляторов и сборку AI-стека под архитектуру NVIDIA Volta (SM 7.0).

**Важно:** Документ описывает две рабочие конфигурации:
- **Конфигурация A (рекомендуемая):** 1Cat-vLLM — форк с FlashAttention-2 для V100 и AWQ 4-bit
- **Конфигурация B (альтернативная):** Официальный vLLM 0.18.x с Triton-ядрами

---

## 1. Настройка и оптимизация OS

Для обеспечения максимальной производительности инференса на базе V100 и сохранения профиля безопасности системы, обновите глобальные флаги оптимизации компилятора GCC.

### Настройка `/etc/portage/make.conf`:

```make
CFLAGS="-O3 -march=broadwell -pipe -flto=auto"
CPU_FLAGS_X86="aes avx avx2 f16c fma3 mmx mmxext pclmul popcnt rdrand sse sse2 sse3 sse4_1 sse4_2 ssse3"
USE="cuda nccl cudnn tensorrt mpi openmp opencl pcie-p2p -X -wayland -gui -dist-kernel"
PYTHON_TARGETS="python3_12"
CXXFLAGS="${CFLAGS}"
MAKEOPTS="-j16"

USE="hardened pic pie nsm tcmalloc native-symlinks cuda"
VIDEO_CARDS="nvidia"
```

> **Примечание по Python:** 1Cat-vLLM предоставляет готовые wheel-пакеты только для Python 3.12. Если требуется Python 3.13, необходимо собирать vLLM из исходников (Конфигурация B).

```bash
emerge --ask --changed-use --deep @world
```

---

## 2. Системные переменные окружения

CUDA 12.8 — единственная стабильная версия для архитектуры Volta в 2026 году. Официальный vLLM 0.20+ переключился на CUDA 13.0, которая помечает sm_70 как legacy.

```bash
# Привязка путей к CUDA 12.8
export CUDA_HOME=/usr/local/cuda-12.8
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}

# Флаги компиляции для архитектуры Volta (см_70)
export TORCH_CUDA_ARCH_LIST="7.0"
export VLLM_CONCURRENT_ARCHES="7.0"
export PYTORCH_NVCC_FLAGS="-arch=sm_70"

# Ограничение параллелизма сборки для стабильности
export MAX_JOBS=4
```

### Различия между конфигурациями:

| Параметр | Конфигурация A (1Cat-vLLM) | Конфигурация B (vLLM 0.18.x) |
|----------|---------------------------|------------------------------|
| FlashAttention | Включён (`FLASH_ATTN_V100`) | Отключён (`VLLM_USE_FLASH_ATTN=0`) |
| Бэкенд внимания | FlashAttention-2 для sm_70 | Triton JIT-ядра |
| Квантизация | AWQ 4-bit через lmdeploy | bitsandbytes |
| Первый запуск | Быстрый (готовые wheel) | 5–10 мин компиляции Triton |

---

## 3. Инициализация окружения Python

```bash
# Создание и активация виртуального окружения
python3 -m venv nt_env
source nt_env/bin/activate

# Обновление менеджеров пакетов и сборщиков
pip install --upgrade pip setuptools wheel ccache
```

---

## 4. Установка PyTorch

Для CUDA 12.8 используется cu128-индекс PyTorch:

```bash
pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu128
```

> **Проверка:** `python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"`
> Должно вывести: `True 12.8`

---

## 5. Установка vLLM

### Конфигурация A: 1Cat-vLLM (рекомендуется)

Форк с восстановленной поддержкой V100, FlashAttention-2 и AWQ 4-bit:

```bash
# Установка готовых wheel-пакетов
python -m pip install --prefer-binary --no-cache-dir \
  --extra-index-url https://download.pytorch.org/whl/cu128 \
  "https://github.com/1CatAI/1Cat-vLLM/releases/download/v1.0.0/flash_attn_v100-1.0.0-cp312-cp312-linux_x86_64.whl" \
  "https://github.com/1CatAI/1Cat-vLLM/releases/download/v1.0.0/vllm-1.0.0-cp312-cp312-linux_x86_64.whl"
```

### Конфигурация B: Официальный vLLM 0.18.x

Последняя версия с нативной поддержкой sm_70. Сборка из исходников:

```bash
# Клонирование официального репозитория
git clone https://github.com/vllm-project/vllm
cd vllm

# Переключение на стабильный релиз
git checkout v0.18.2

# Установка сборочных зависимостей
pip install -r requirements-build.txt

# Компиляция CUDA-ядер PagedAttention под sm_70
# FlashAttention отключён, так как требует sm_80+
TORCH_CUDA_ARCH_LIST="7.0" VLLM_USE_FLASH_ATTN=0 \
  pip install --no-build-isolation -e .
cd ..
```

### Альтернативный бэкенд: XFormers

```bash
cd NeuralTower/Software/Linux

# Установка зависимостей
pip install -r requirements.txt

# XFormers как альтернатива Triton для V100
TORCH_CUDA_ARCH_LIST="7.0" pip install xformers --no-deps
```

---

## 6. Правила запуска инференса

Графические процессоры Volta (V100) аппаратно не поддерживают `bfloat16` (медленная программная эмуляция).

**Все модели должны запускаться с `--dtype float16`.**

### Конфигурация A: 1Cat-vLLM

```bash
python -m vllm.entrypoints.openai.api_server \
  --model /path/to/model \
  --attention-backend FLASH_ATTN_V100 \
  --tensor-parallel-size 4 \
  --dtype float16 \
  --gpu-memory-utilization 0.88 \
  --max-model-len 262144 \
  --max-num-seqs 1 \
  --max-num-batched-tokens 16384
```

### Конфигурация B: Официальный vLLM 0.18.x

```bash
export VLLM_ATTENTION_BACKEND=TRITON_ATTN
export VLLM_TENSORRT_LLM_TIMEOUT=600

python -m vllm.entrypoints.openai.api_server \
  --model /path/to/model \
  --tensor-parallel-size 4 \
  --dtype float16 \
  --gpu-memory-utilization 0.95 \
  --swap-space 64 \
  --max-model-len 32768
```

### Для больших моделей (70B+)

```bash
# Конфигурация A: AWQ квантизация
--quantization awq --dtype float16

# Конфигурация B: bitsandbytes
--quantization bitsandbytes --load-in-4bit
```

---

## Справочная таблица параметров

| Параметр | Конфигурация A | Конфигурация B |
|----------|---------------|---------------|
| `--tensor-parallel-size` | 4 | 4 |
| `--gpu-memory-utilization` | 0.88 | 0.95 |
| `--max-model-len` | 262144 | 32768 |
| `--attention-backend` | FLASH_ATTN_V100 | TRITON_ATTN |
| `--quantization` | awq | bitsandbytes |
| Python | 3.12 | 3.12 или 3.13 |
| CUDA | 12.8 | 12.8 |
