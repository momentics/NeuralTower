#!/bin/bash
# Инициализация директории кэша SGLang и прав доступа

CACHE_DIR="${KV_CACHE_PATH:-/mnt/optane_u2/sglang_kv_cache}"

echo "Creating cache directory: $CACHE_DIR"
mkdir -p "$CACHE_DIR"

echo "Setting permissions..."
chmod 777 "$CACHE_DIR"

echo "Checking if directory exists and is writable..."
if [ -w "$CACHE_DIR" ]; then
    echo "[OK] Cache directory ready: $CACHE_DIR"
else
    echo "[ERROR] Cannot write to $CACHE_DIR"
    exit 1
fi

echo "Done."