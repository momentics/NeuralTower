# Полная сборка окружения NeuralTower под CUDA 13.1 для GPU V100 (SXM2 32GB) в Gentoo Linux Hardened

Данная инструкция описывает процесс развертывания, включая базовую настройку и оптимизацию Gentoo, конфигурацию компиляторов и ручную сборку AI-стека под архитектуру NVIDIA Volta (SM 7.0).

---

## 1. Настройка и оптимизация OS

Для обеспечения максимальной производительности инференса на базе V100 и сохранения профиля безопасности системы, обновите глобальные флаги оптимизации компилятора GCC.

### Настройка `/etc/portage/make.conf`:
Параметры сборки:
```make
CFLAGS="-O3 -march=broadwell -pipe -flto=auto"
CPU_FLAGS_X86="aes avx avx2 f16c fma3 mmx mmxext pclmul popcnt rdrand sse sse2 sse3 sse4_1 sse4_2 ssse3"
USE="cuda nccl cudnn tensorrt mpi openmp opencl pcie-p2p -X -wayland -gui -dist-kernel"
PYTHON_TARGETS="python3_13"
CXXFLAGS="${CFLAGS}"
MAKEOPTS="-j16"

USE="hardened pic pie nsm tcmalloc native-symlinks cuda"
VIDEO_CARDS="nvidia"
```

```bash
emerge --ask --changed-use --deep @world
```

---

## 2. Системные переменные окружения для CUDA 13.1

Поскольку пакеты vLLM под CUDA 13.x по умолчанию собираются без учета архитектур прошлых поколений, необходимо вручную ограничить инструкции компилятора `nvcc` уровнем архитектуры Volta (SM70) и отключить несовместимые модули (например, FlashAttention).

Выполните экспорт переменных в сессии терминала:
```bash
# Привязка путей к установленному дистрибутиву CUDA 13.1 в Gentoo
export CUDA_HOME=/usr/local/cuda-13.1
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Жесткое ограничение целевой архитектуры компилятора (Volta SM70)
export TORCH_CUDA_ARCH_LIST="7.0"
export VLLM_CONCURRENT_ARCHES="7.0"
export PYTORCH_NVCC_FLAGS="-arch=sm_70"

# Аппаратное отключение модулей FlashAttention-2/3 (требуют SM80+)
export VLLM_TARGET_DEVICE="cuda"
export VLLM_USE_FLASH_ATTN=0
export vllm_flash_attn=0

export MAX_JOBS=4
```

---

## 3. Инициализация окружения Python

Bзолированная среда выполнения:

```bash
# Создание и активация виртуального окружения
python3 -m venv nt_env
source nt_env/bin/activate

# Обновление менеджеров пакетов и сборщиков
pip install --upgrade pip setuptools wheel ccache
```

---

## 4. Установка PyTorch

Для работы драйвера CUDA 13.1 со старыми картами рекомендуется использовать стабильный cu121-рантайм, который полностью поддерживается драйвером на архитектуре Volta:

```bash
pip install torch torchvision torchaudio --index-url pytorch.org
```

---

## 5. Сборка vLLM из исходных кодов под V100 (SM70)

Использование готовых пакетов `pip install vllm` в среде CUDA 13.1 приведет к ошибке выполнения (*Illegal Instruction*) на V100. Сборка выполняется строго из репозитория совместимой ветки `0.18.x`.

```bash
# Клонирование официального репозитория движка
git clone https://github.com/vllm-project/vllm
cd vllm

# Переключение на стабильный релиз, поддерживаемый архитектурой NeuralTower
git checkout v0.18.2

# Установка сборочных зависимостей
pip install -r requirements-build.txt

# Компиляция кастомных CUDA-ядер PagedAttention под архитектуру SM70
TORCH_CUDA_ARCH_LIST="7.0" VLLM_USE_FLASH_ATTN=0 pip install --no-build-isolation -e .
cd ..
```

---


```bash
cd NeuralTower/Software/Linux

# Установка зависимостей
pip install -r requirements.txt

# Установка XFormers из исходников в качестве альтернативного бэкенда внимания для V100
TORCH_CUDA_ARCH_LIST="7.0" pip install xformers --no-deps
```

---

## 7. Правила запуска инференса

Графические процессоры Volta (V100) аппаратно не поддерживают вычисления в формате данных `bfloat16` (выполняется медленная программная эмуляция). 

**Все модели в рамках проекта NeuralTower должны принудительно запускаться в режиме float16 (`--dtype float16`).**

### Команда для запуска инференс-сервера:
```bash
python3 -m vllm.entrypoints.openai.api_server \
    --model /path/to/neural_tower_model \
    --tensor-parallel-size 1 \
    --dtype float16 \
    --gpu-memory-utilization 0.92 \
    --max-model-len 4096
```

Для больших моделей обязательно используйте AWQ-квантование:
```bash
--quantization awq --dtype float16
```
