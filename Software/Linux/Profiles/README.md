# Памятка по сборке для системного инженера

## Создание Performance-ядра

```bash
cd /usr/src/linux-performance
# Применяем патч производительности performance_kernel.patch
make oldconfig
make -j$(nproc)
cp arch/x86/boot/bzImage /boot/vmlinuz-performance
```

## Создание Hardened-ядра

```bash
cd /usr/src/linux-hardened
# Применяем патч безопасности hardened_kernel.patch
make oldconfig
make -j$(nproc)
cp arch/x86/boot/bzImage /boot/vmlinuz-hardened
```

## Обновление GRUB

После копирования бинарников ядер запустите утилиту автоматической сборки конфигурации загрузчика:

```bash
grub-mkconfig -o /boot/grub/grub.cfg
```
