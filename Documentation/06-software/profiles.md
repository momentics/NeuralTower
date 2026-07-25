# Памятка по сборке для системного инженера

## Создание Performance-ядра

Набор флагов применяется поверх sys-kernel/gentoo-sources или sys-kernel/vanilla-sources. Убирает защитные барьеры и накладные расходы для максимальной скорости обработки KV-кэша.

```bash
cd /usr/src/linux-performance
# Применяем патч производительности performance_kernel.patch
make oldconfig
make -j$(nproc)
cp arch/x86/boot/bzImage /boot/vmlinuz-performance
```

## Создание Hardened-ядра

Набор флагов применяется поверх sys-kernel/hardened-sources. Включает механизмы защиты от эксплуатации уязвимостей: KASLR, контроль копирования данных, защита стека, lockdown-режим.

```bash
cd /usr/src/linux-hardened
# Применяем патч безопасности hardened_kernel.patch
make oldconfig
make -j$(nproc)
cp arch/x86/boot/bzImage /boot/vmlinuz-hardened
```

## Конфигурирование GRUB

`GRUB_DEFAULT=saved` указывает загрузчику использовать последний выбранный профиль из файла `grubenv`, а не жёстко первый пункт.
`GRUB_SAVEDEFAULT=true` заставляет GRUB автоматически сохранять выбранный пункт в `grubenv`.

```ini
# Использование последнего выбранного профиля
GRUB_DEFAULT=saved

# Автоматическое сохранение выбранного пункта
GRUB_SAVEDEFAULT=true
```

```ini
# /boot/grub/grub.cfg

menuentry "NeuralTower - PERFORMANCE (Максимальная скорость)" {
    linux /boot/vmlinuz-performance root=/dev/sda3 console=ttyS0,115200n8 mitigations=off
}

menuentry "NeuralTower - HARDENED (Защищённый профиль)" {
    linux /boot/vmlinuz-hardened root=/dev/sda3 console=ttyS0,115200n8 mitigations=auto
}
```

## Пересборка конфигурации GRUB

После копирования ядер обновите конфигурацию загрузчика:

```bash
grub-mkconfig -o /boot/grub/grub.cfg
```
