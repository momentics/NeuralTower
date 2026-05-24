# Памятка по сборке для системного инженера

## Создание Performance-ядра

Этот набор флагов применяется поверх стандартных исходных кодов ядра sys-kernel/gentoo-sources или sys-kernel/vanilla-sources. Он полностью вырезает защитные барьеры и накладные расходы ради достижения максимального темпа прокачки терабайтного KV-кэша моделей.

```bash
cd /usr/src/linux-performance
# Применяем патч производительности performance_kernel.patch
make oldconfig
make -j$(nproc)
cp arch/x86/boot/bzImage /boot/vmlinuz-performance
```

## Создание Hardened-ядра

Этот набор флагов применяется поверх исходных кодов ядра защищенного профиля sys-kernel/hardened-sources. Он разворачивает полный комплекс механизмов противодействия эксплуатации уязвимостей (KASLR, контроль копирования данных, защита стека и lockdown-режим).

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
