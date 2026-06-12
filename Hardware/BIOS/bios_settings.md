# Конфигурация BIOS и оптимизация системной логики

Корректная инициализация четырех серверных ускорителей Tesla V100 на десктопной платформе LGA 2011-3 требует специфической настройки параметров BIOS. Основная задача заключается в расширении адресного пространства для работы с видеопамятью HBM2 (128 ГБ) и системной памятью (256 ГБ DDR4 32GB 2400 ECC REG RDimm), а также обеспечении стабильной связи через каскад мостов PLX.

## 1. Подготовка адресного пространства и шины PCIe

### Above 4G Decoding

Главным условием функционирования системы является активация режима Above 4G Decoding. Данная настройка позволяет операционной системе адресовать видеопамять ускорителей за пределами классического 32-битного лимита, что критически важно для инициализации всех четырех модулей HBM2 (итого 128 ГБ). Без этого параметра система не сможет распределить ресурсы для мезонинов, что приведет к ошибкам на этапе загрузки ядра.

| Параметр | Путь в BIOS | Значение |
| --- | --- | --- |
| Above 4G Decoding | Boot → Boot Configuration → Above 4G Decoding | [Enabled] |

### Скорость слотов PCIe

Для стабилизации высокочастотных сигналов, проходящих через восемь шлейфов SlimSAS, в настройках шины PCIe необходимо принудительно зафиксировать режим Gen3. Автоматическое определение поколения шины на столь длинных и сложных линиях часто приводит к деградации скорости или потере связи с отдельными GPU. Бифуркация (Bifurcation x8/x8) не требуется: каждый слот x16 через пассивный адаптер разветвляется на два SlimSAS 8i, идущие к одному GPU на мезонине, где потоки снова объединяются в x16 для кристалла V100. Коммутатор PLX видит одно устройство x16 на каждый слот.

| Параметр | Путь в BIOS | Значение |
| --- | --- | --- |
| PCIEX16_1 Link Speed | Advanced → System Agent Configuration → NB PCI-E Configuration → PCIEX16_1 Link Speed | [Gen3] |
| PCIEX16_2 Link Speed | Advanced → System Agent Configuration → NB PCI-E Configuration → PCIEX16_2 Link Speed | [Gen3] |
| PCIEX16_3 Link Speed | Advanced → System Agent Configuration → NB PCI-E Configuration → PCIEX16_3 Link Speed | [Gen3] |
| PCIEX16_4 Link Speed | Advanced → System Agent Configuration → NB PCI-E Configuration → PCIEX16_4 Link Speed | [Gen3] |
| PCIEX16_5 Link Speed | Advanced → System Agent Configuration → NB PCI-E Configuration → PCIEX16_5 Link Speed | [Gen3] |
| PCIEX16_6 Link Speed | Advanced → System Agent Configuration → NB PCI-E Configuration → PCIEX16_6 Link Speed | [Gen3] |
| PCIEX16_7 Link Speed | Advanced → System Agent Configuration → NB PCI-E Configuration → PCIEX16_7 Link Speed | [Gen3] |
| PCIe Speed | Advanced → CPU Configuration → PCI Express Configuration → PCIe Speed | [Gen3] |

## 2. Управление задержками и энергопотреблением

### Intel VT-d

Для минимизации задержек при обмене данными между GPU и NVMe-накопителем рекомендуется отключить технологии виртуализации ввода-вывода, такие как VT-d или IOMMU, если проект не предполагает использование проброса устройств в виртуальные машины. Это избавляет систему от лишних уровней трансляции адресов и повышает общую отзывчивость при инференции.

| Параметр | Путь в BIOS | Значение |
| --- | --- | --- |
| Intel VT for Directed I/O (VT-d) | Advanced → System Agent Configuration → Intel VT for Directed I/O (VT-d) → Intel VT for Directed I/O (VT-d) | [Disabled] |

### CPU C-States

Параметры энергосбережения процессора (C-States) следует перевести в режим высокой производительности или полностью деактивировать. Это предотвращает нежелательные колебания частот и напряжения на шине PCIe при резких сменах нагрузки, которые характерны для работы алгоритмов vLLM.

| Параметр | Путь в BIOS | Значение |
| --- | --- | --- |
| CPU states | Advanced → CPU Configuration → CPU Power Management Configuration → CPU states | [Disabled] |
| Package C State Support | Advanced → CPU Configuration → CPU Power Management Configuration → Package C State Support | [C0/C1] |

### Secure Boot и CSM

Дополнительно необходимо убедиться, что приоритет загрузки установлен на UEFI-режим, а функции Secure Boot настроены на работу с пользовательскими ключами или отключены, что упрощает установку и загрузку ядра Gentoo Linux.

| Параметр | Путь в BIOS | Значение |
| --- | --- | --- |
| Launch CSM | Boot → Boot Configuration → CSM → Launch CSM | [Disabled] |
| OS Type | Boot → Boot Configuration → Secure Boot → OS Type | [Other OS] |

## 3. Верификация и сохранение профиля

После внесения всех изменений необходимо произвести холодный старт системы. Первичная инициализация четырех карт может занять больше времени, чем обычно, так как мосты PLX должны согласовать тайминги всех соединений. В случае успешного прохождения POST-кодов настройки следует сохранить в отдельный профиль через меню ASUS O.C. Profile (Tool → ASUS O.C. Profile). Это позволит быстро восстановить работоспособность системы после сброса параметров или замены батареи CMOS, исключая необходимость повторной ручной настройки сложных параметров шины данных.
