```bash
# 1. Собираем Docker-образ из созданных файлов
docker build -t gpu-tester .

# 2. Запускаем контейнер с пробросом ВСЕХ GPU устройств (--gpus all)
docker run --rm --gpus all --privileged gpu-tester

```

