# NeuralTower

<img src="./Docs/Images/logo.png" width="100" align="left" alt="Логотип проекта NeuralTower"> NeuralTower - открытый инженерный проект настольной рабочей станции на четырех NVIDIA Tesla V100 SXM2 32 GB. Цель проекта - собрать локальный узел с 128 GB HBM2 для инференса и экспериментов с большими моделями без постоянной зависимости от облака.
<br clear="left" />

Проект находится в стадии проектирования и доводки. В репозитории отдельно лежат расчеты, механика, электрическая часть, подготовка железа, программная среда и статьи о проекте. Если обзорный текст расходится с инженерным документом, для сборки нужно использовать инженерный документ.

## Быстрая навигация

| Раздел | Назначение |
| --- | --- |
| [Docs/project_status.md](./Docs/project_status.md) | Текущий статус узлов, неподтвержденные гипотезы и план первичной проверки |
| [Docs/BOM/bom_list.md](./Docs/BOM/bom_list.md) | Перечень компонентов, материалов и закупочных позиций |
| [Docs/Calculations/air_dynamics.md](./Docs/Calculations/air_dynamics.md) | Расчет воздушной части V-CORE |
| [CAD/Frame/frame_assembly.md](./CAD/Frame/frame_assembly.md) | Нарезка профиля, рельсы и силовые поперечины каркаса |
| [CAD/Mounts/mounting_hardware.md](./CAD/Mounts/mounting_hardware.md) | Канонический порядок сборки нижнего отсека |
| [CAD/Deck/deck_layout.md](./CAD/Deck/deck_layout.md) | Геометрия палубы, сопел и технологических проходов |
| [Electrical/Pinouts/slimsas_mapping.md](./Electrical/Pinouts/slimsas_mapping.md) | Топология SlimSAS, слоты PCIe и порядок GPU |
| [Hardware/BIOS/bios_settings.md](./Hardware/BIOS/bios_settings.md) | Настройки BIOS для V100, PLX и PCIe |
| [Software/Linux/system_setup.md](./Software/Linux/system_setup.md) | Порядок подготовки ОС и первого запуска |
| [Diagnosis/V100-SXM2-32G](./Diagnosis/V100-SXM2-32G/) | Контейнер диагностики четырех V100 SXM2 |

## Архитектура

Система строится вокруг четырех Tesla V100 SXM2, установленных на двух SXM2 carrier board. Внутри каждого мезонина пара GPU связана NVLink 2.0, а межмезонинный обмен идет через PCIe 3.0 x16, SlimSAS SFF-8654 8i и PLX-коммутаторы материнской платы ASUS X99-E WS.

Основной инженерный компромисс проекта: V100 уже не современная архитектура, но дает большой объем HBM2 на вторичном рынке. Для программного стека это означает обязательную работу с ограничениями Volta `sm_70`: CUDA 12.8, FP16 как базовый тип данных и отдельная стратегия для vLLM.

## Охлаждение V-CORE

V-CORE - рабочее название схемы охлаждения, где жидкостный контур снимает основную тепловую нагрузку с CPU и GPU, а нижний отсек корпуса работает как камера избыточного давления. Воздух проходит через радиаторы СЖО, попадает в герметичный КВД и выходит через калиброванные сопла палубы к VRM, обратным сторонам плат и зонам, не закрытым водоблоками. Два блока питания HX1000 находятся в изолированных боковых отсеках и не используют воздух КВД.

Основные документы по этой теме:

- механика палубы: [CAD/Deck/deck_layout.md](./CAD/Deck/deck_layout.md);
- аэродинамический расчет: [Docs/Calculations/air_dynamics.md](./Docs/Calculations/air_dynamics.md);
- гидравлика СЖО: [Docs/Calculations/coolant_hydraulics.md](./Docs/Calculations/coolant_hydraulics.md);
- объем теплоносителя: [Docs/Calculations/coolant_volume.md](./Docs/Calculations/coolant_volume.md).

## Программный стек

Основной путь развертывания: Gentoo Linux, CUDA 12.8, NVIDIA driver 580+, Python 3.12 и 1Cat-vLLM для восстановления рабочей поддержки V100. Альтернативный путь - официальный vLLM ветки `0.18.x` с Triton-бэкендом, если форк 1Cat-vLLM не подходит.

Стартовые документы:

- [Software/Linux/system_setup.md](./Software/Linux/system_setup.md) - порядок подготовки системы и ссылки на подробные инструкции;
- [Software/Linux/gentoo_optimization.md](./Software/Linux/gentoo_optimization.md) - параметры Gentoo и ядра;
- [Software/Linux/world_build.md](./Software/Linux/world_build.md) - воспроизводимая сборка окружения;
- [Software/Linux/vllm_optimization.md](./Software/Linux/vllm_optimization.md) - запуск vLLM, TP/PP, NVMe swap и NCCL.

## Безопасность

В проекте используются высокие токи, два блока питания, жидкостное охлаждение и дорогое серверное оборудование. До подачи питания обязательны проверка распиновок, прозвонка переходников, контроль общей земли между БП и рамой, наружный доступ к выключателям HX1000, тест герметичности СЖО и проверка работы помп.

Связанные документы:

- [Electrical/Pinouts/adapter_spec.md](./Electrical/Pinouts/adapter_spec.md);
- [Electrical/Wiring/power_distribution.md](./Electrical/Wiring/power_distribution.md);
- [Electrical/Wiring/grounding_guide.md](./Electrical/Wiring/grounding_guide.md);
- [Docs/project_status.md](./Docs/project_status.md).

## Структура репозитория

```text
NeuralTower/
├── Articles/              # публикации и черновики статей
├── CAD/                   # механическая компоновка и сборка
├── Diagnosis/             # аппаратные тесты GPU
├── Docs/
│   ├── BOM/               # перечень компонентов
│   ├── Calculations/      # расчетные записки
│   └── Images/            # логотип, схемы и будущие фотографии
├── Electrical/            # питание, земля, распиновки
├── Hardware/              # GPU, BIOS, аппаратная подготовка
├── Manuals/               # внешние мануалы и справочные материалы
└── Software/              # ОС, ML-стек, мониторинг
```

## Связь

Группа в Telegram: [@NeuralTower](https://t.me/NeuralTower)

<p align="left"><img src="./Docs/Images/Telegram.png" width="150" height="150" alt="Группа Telegram проекта NeuralTower"></p>
