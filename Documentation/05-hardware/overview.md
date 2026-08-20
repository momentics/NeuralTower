# Подготовка аппаратной части

Раздел описывает подготовку аппаратной части системы NeuralTower: подготовку GPU и настройку BIOS для четырёх ускорителей Tesla V100 SXM2 на настольной платформе LGA 2011-3.

## Кратко: подготовка GPU

Модули Tesla V100 SXM2 требуют демонтажа штатных радиаторов, очистки кристаллов GPU и памяти HBM2 и установки водоблоков Speedier XF-001-CO (140 x 80 x 30 мм, 300W TDP). Для долгосрочной надёжности критичны правильный выбор термоинтерфейса и равномерное усилие прижима.

## Кратко: настройки BIOS

| Параметр | Путь в BIOS | Значение |
| --- | --- | --- |
| Above 4G Decoding | Advanced → PCI Subsystem Settings → Above 4G Decoding | Enabled |
| PCIEX16_1-7 Link Speed | Advanced → System Agent Configuration → NB PCI-E Configuration | Gen3 |
| PCIe Speed | Advanced → CPU Configuration → PCI Express Configuration → PCIe Speed | Gen3 |
| Intel VT-d | Advanced → System Agent Configuration → Intel VT-d | Disabled |
| CPU states | Advanced → CPU Configuration → CPU Power Management Configuration | Disabled |
| Package C State Support | Advanced → CPU Configuration → CPU Power Management Configuration | C0/C1 |
| Launch CSM | Boot → Boot Configuration → CSM → Launch CSM | Disabled |
| OS Type | Boot → Boot Configuration → Secure Boot → OS Type | Other OS |

## Подробные руководства

- [Подготовка GPU](./gpu-preparation.md) — демонтаж, установка водоблоков, интеграция в мезонин
- [Настройки BIOS](./bios-settings.md) — полная конфигурация BIOS и оптимизация системной логики
