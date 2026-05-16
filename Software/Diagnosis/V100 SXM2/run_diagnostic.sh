#!/bin/bash
set -e

echo "=========================================================="
echo "    NEURALTOWER: ВАЛИДАЦИЯ 4x NVIDIA TESLA V100 SXM2      "
echo "=========================================================="

# 1. Проверка доступности драйверов и nvidia-smi
if ! command -v nvidia-smi &> /dev/null; then
    echo "[ОШИБКА]: Утилита nvidia-smi не найдена. Проверьте nvidia-container-toolkit на хосте."
    exit 1
fi

# 2. Проверка количества видеокарт (Ожидаем строго 4 шт.)
GPU_COUNT=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
echo "Обнаружено GPU в системе: $GPU_COUNT"

if [ "$GPU_COUNT" -ne 4 ]; then
    echo "[ОШИБКА]: Ожидалось 4 видеокарты Tesla V100, обнаружено: $GPU_COUNT."
    echo "Проверьте физическое подключение карт, питание SXM2 и настройки Above 4G Decoding в BIOS."
    exit 1
fi

echo -e "\nСписок тестируемых устройств:"
nvidia-smi --query-gpu=index,name,serial,uuid,memory.total --format=csv
echo "----------------------------------------------------------"

# 3. Важнейший экспресс-анализ б/у карт: Проверка "отбракованных" страниц HBM2 (Page Retirement)
echo -e "\n[ШАГ 1/3]: Анализ деградации памяти (Retired Pages)..."
RETIRED_ERRORS=$(nvidia-smi -q -d PAGE_RETIREMENT | grep -E "Double Bit|Single Bit" | grep -v "0" || true)

if [ ! -z "$RETIRED_ERRORS" ]; then
    echo "[ВНИМАНИЕ]: Обнаружены аппаратно изолированные (отбракованные) области памяти HBM2:"
    nvidia-smi -q -d PAGE_RETIREMENT | grep -E "GPU|Sectors|Double Bit|Single Bit"
    echo "Предупреждение: Карта имеет износ памяти, но мы продолжаем комплексный тест..."
else
    echo "Аппаратных дефектов памяти на уровне контроллера не обнаружено."
fi

# 4. Инициализация движка DCGM
echo -e "\n[ШАГ 2/3]: Запуск фонового менеджера nv-hostengine..."
nv-hostengine
sleep 3 # Время на инициализацию демона

# 5. Запуск комплексной стресс-диагностики DCGM Level 3
echo -e "\n[ШАГ 3/3]: Запуск глубокого диагностического пакета DCGM (Level 3)..."
echo "Этот процесс займет от 5 до 15 минут. Проверяются шина, NVLink, CUDA ядра и лимиты питания."
echo "Пожалуйста, подождите..."
echo "----------------------------------------------------------"

# Запускаем диагностику для всех групп (ID 0,1,2,3)
set +e
dcgmi diag -r 3 -a > /tmp/dcgm_full_report.txt
DIAG_EXIT_CODE=$?
set -e

# Выводим полный отчет в лог контейнера
cat /tmp/dcgm_full_report.txt
echo "----------------------------------------------------------"

# 6. Финальная оценка результатов
if [ $DIAG_EXIT_CODE -eq 0 ]; then
    echo "[УСПЕХ]: Все 4 карты Tesla V100 SXM2 успешно прошли глубокое тестирование!"
    exit 0
else
    echo "[ОШИБКА]: Тестирование DCGM завершилось неудачей. Одна или несколько карт нестабильны."
    exit $DIAG_EXIT_CODE
fi
