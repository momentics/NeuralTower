# Процедура развертывания и сборки системы на базе Stage3 Hardened

Для проекта NeuralTower используется профиль Hardened Gentoo, обеспечивающий усиленную защиту адресного пространства памяти, что критично при эксплуатации 128 ГБ HBM2 и активном использовании механизма свопа на NVMe.

## 1. Подготовка окружения

После загрузки актуального образа `stage3-amd64-hardened-nomultilib` и настройки `chroot`, необходимо установить базовые параметры в `/etc/portage/make.conf`, ориентированные на вычислительную мощность Xeon E5-2699v4:

```bash
COMMON_FLAGS="-O3 -march=broadwell -pipe -flto=auto"
CPU_FLAGS_X86="aes avx avx2 f16c fma3 mmx mmxext pclmul popcnt rdrand sse sse2 sse3 sse4_1 sse4_2 ssse3"
USE="cuda nccl cudnn tensorrt mpi openmp opencl pcie-p2p -X -wayland -gui -dist-kernel"
PYTHON_TARGETS="python3_13"
VIDEO_CARDS="nvidia"
```

## 2. Синхронизация и выбор профиля

Перед началом глобальной сборки необходимо выбрать актуальный профиль, поддерживающий современные стандарты безопасности и Hardened-инструментарий:

```bash
emerge --sync
eselect profile set default/linux/amd64/23.0/hardened
```

## 3. Финальная команда сборки мира

Данная команда инициирует полную пересборку всех системных компонентов и библиотек (включая glibc, GCC и системные зависимости Python 3.13) с учетом флагов оптимизации под процессор и CUDA 13.x. Это гарантирует отсутствие в системе лишних бинарных модулей и максимальную производительность вычислительного стека.

```bash
emerge --ask --verbose --update --deep --newuse --with-bdeps=y --backtrack=100 @world
```

## 4. Сборка специфического стека NeuralTower

После того как базовая система оптимизирована, устанавливаются ключевые пакеты для управления графическими ускорителями и контейнеризацией:

```bash
emerge --ask dev-util/nvidia-cuda-toolkit sci-libs/cudnn sci-libs/nccl app-containers/docker app-containers/nvidia-container-toolkit
```

## Ожидаемый результат

По завершении процесса вся операционная среда NeuralTower будет представлять собой единый бинарный монолит, скомпилированный под инструкции AVX2 и использующий механизмы защиты памяти Hardened-ядра. Такой подход сводит к минимуму накладные расходы при управлении очередями инференса в vLLM и обеспечивает максимальную пропускную способность шины PCIe при обмене данными между GPU и NVMe-накопителем.
