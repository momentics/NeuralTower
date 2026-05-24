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

## Конфигурирование GRUB

GRUB_DEFAULT=saved указывает загрузчику при старте не запускать жестко первый пункт по порядку, а смотреть в специальный текстовый файл среды (grubenv), где хранится имя последнего запущенного профиля.
GRUB_SAVEDEFAULT=true заставляет GRUB автоматически перезаписывать этот файл каждый раз, когда физически выбираете в меню другую строчку и нажимаете Enter.

```ini
# Заставляем GRUB использовать сохраненное значение по умолчанию
GRUB_DEFAULT=saved

# Включаем механизм записи последнего успешно выбранного пункта в память
GRUB_SAVEDEFAULT=true
```

```ini
# /boot/grub/grub.cfg

menuentry "NeuralTower - PERFORMANCE PROFILE (Maximum Speed)" {
    linux /boot/vmlinuz-performance root=/dev/sda3 console=ttyS0,115200n8 mitigations=off
}

menuentry "NeuralTower - HARDENED PROFILE (Public Internet Secure)" {
    linux /boot/vmlinuz-hardened root=/dev/sda3 console=ttyS0,115200n8 mitigations=auto
}
```

## Пересборка конфигурации GRUB

После копирования бинарников ядер запустите утилиту автоматической сборки конфигурации загрузчика:

```bash
grub-mkconfig -o /boot/grub/grub.cfg
```
