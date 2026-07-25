# ASUS X99-E WS — Материнская плата

## 1. Общие сведения

| Параметр | Значение |
|---|---|
| Модель | ASUS X99-E WS |
| Форм-фактор | E-ATX |
| Сокет | LGA 2011-3 |
| Чипсет | Intel C612/X99 |
| Версия BIOS | REV 1.01 |

## 2. Сокет и процессор

- **Сокет:** LGA 2011-3 (Socket R3)
- **Совместимые процессоры:** Intel Xeon E5 v4 (14nm)
- **Максимальная конфигурация:** 2 процессора

## 3. Память

| Параметр | Значение |
|---|---|
| Слоты DIMM | 16 (8 на каждый процессор) |
| Тип памяти | DDR4 ECC Registered |
| Каналы | 4-канальный (на каждый процессор) |
| Группы | DIMM_A1–A4 / DIMM_B1–B4 (CPU1), DIMM_D1–D4 / DIMM_C1–C4 (CPU2) |

## 4. Слоты расширения

| Слот | Тип | Линии |
|---|---|---|
| PCIEX16_1 | PCIe 3.0 x16 | x16 (от CPU1) |
| PCIEX16_2 | PCIe 3.0 x16 | x16 (от CPU2) |
| PCIEX16_3 | PCIe 3.0 x16 | x16 (от PLX) |
| PCIEX16_4 | PCIe 3.0 x16 | x16 (от PLX) |

### 4.1. PLX PEX 8747

Плата оснащена чипом PLX PEX 8747, который мультиплексирует линии PCIe для обеспечения дополнительных слотов x16.

## 5. Разъёмы питания

| Разъём | Назначение |
|---|---|
| ATX 24-pin | Основное питание |
| EATXPWR 8-pin | Дополнительное питание (ATX 12V) |
| CPU 8-pin (EPS) | Питание процессора (CPU1) |
| CPU 8-pin (EPS) | Питание процессора (CPU2) |

## 6. Хранение данных

- **SATA III (6 Гбит/с):** 8 портов (Intel + ASMedia)
- **SATA Express:** 2 порта (SATA6G_9 / SATA6G_10, разделяют полосы)
- **M.2 x4:** 1 слот (PCIe 3.0 x4, NVMe)

## 7. Сеть

- **Intel Ethernet:** 2 порта 10 Гбит/с (Intel X520-D2)
- **Intel Ethernet:** 1 порт 1 Гбит/с (Intel i210)

## 8. Аудио

- **Кодек:** ALC1150 (Crystal Sound 2)

## 9. Управление и переключатели

- **TPU LED:** индикатор статуса
- **CPU_OPT / CHA_FAN:** разъёмы вентиляторов
- **Power / Reset:** кнопки на плате
- **POST-индикатор:** 2-разрядный дисплей

## 10. Примечания

**Source files:** `Manuals/ASUS-X99-E-WS/` — 2 PDF-файла (ASUS-X99-E-WS.pdf, Материнская-плата-Asus-X99-E-WS.pdf) и 17 JPEG/PNG-изображений (3dview-1.jpg, 3dview-2.jpg, aida-fpu.png, audio.jpg, box.jpg, complect.jpg, cpu-z.png, front.jpg, lan.jpg, m2.jpg, plx.jpg, post.jpg, power-connector.jpg, radiator-1.jpg, radiator-2.jpg, sata.jpg, socket.jpg, switches.jpg, tpu.jpg, vrm.jpg).
