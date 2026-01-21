# Быстрые команды для AG-Backtester

## Запуск стратегий

```bash
# Активировать окружение (нужно делать каждый раз)
source .venv/bin/activate

# Запустить шаблон стратегии
python strategies/my_strategy.py

# Запустить momentum стратегию
python strategies/momentum_strategy.py

# Запустить debug стратегию (для отладки)
python strategies/debug_strategy.py

# Запустить с конкретным файлом данных
python strategies/momentum_strategy.py examples/data/btcusdt_aggtrades_1m.csv
```

## Без активации venv

```bash
# Использовать Python из venv напрямую
.venv/bin/python strategies/my_strategy.py
.venv/bin/python strategies/momentum_strategy.py
.venv/bin/python strategies/debug_strategy.py
```

## Работа с данными

```bash
# Загрузить данные с Binance (последний час)
.venv/bin/python scripts/download_binance_data.py BTCUSDT

# Сгенерировать синтетические данные
.venv/bin/python scripts/generate_test_data.py

# Запустить пример с автоконвертацией в Parquet
.venv/bin/python examples/run_backtest.py \
  --input examples/data/btcusdt_aggtrades_1m.csv \
  --auto-ticksize \
  --bucket-ms 1000
```

## Тестирование

```bash
# Тест исправленного engine
.venv/bin/python scripts/test_engine_fix.py

# Benchmark производительности
.venv/bin/python benchmark_v0.py
```

## Пересборка после изменений в C/Rust

```bash
source .venv/bin/activate
maturin develop --release -m crates/ag-core/Cargo.toml
```

## Просмотр результатов

```bash
# Открыть tearsheet
open outputs/momentum_tearsheet.png

# Посмотреть метрики
cat outputs/metrics.json

# Посмотреть equity curve
head outputs/equity.csv
```

## Структура файлов

```
ag-kernel/
├── strategies/              # ← Ваши стратегии
│   ├── my_strategy.py      # Шаблон для новых стратегий
│   ├── momentum_strategy.py # Рабочий пример
│   └── debug_strategy.py   # Для отладки
├── scripts/                # ← Утилиты
│   ├── test_engine_fix.py
│   ├── download_binance_data.py
│   └── generate_test_data.py
├── examples/               # ← Примеры и данные
│   ├── run_backtest.py
│   └── data/
│       ├── btcusdt_aggtrades_1m.csv
│       └── btcusdt_aggtrades_sample.parquet
├── outputs/                # ← Результаты
│   ├── momentum_tearsheet.png
│   ├── metrics.json
│   └── equity.csv
└── QUICK_START.md          # ← Полная документация
```

## Быстрый старт

```bash
# 1. Активировать venv
source .venv/bin/activate

# 2. Запустить пример
python strategies/momentum_strategy.py

# 3. Посмотреть результат
open outputs/momentum_tearsheet.png

# 4. Создать свою стратегию
cp strategies/my_strategy.py strategies/my_custom_strategy.py
# Редактировать my_custom_strategy.py
python strategies/my_custom_strategy.py
```

## Troubleshooting

### ModuleNotFoundError: No module named 'ag_backtester'

Используйте `.venv/bin/python` или активируйте venv:
```bash
source .venv/bin/activate
```

### ModuleNotFoundError: No module named 'pandas'

Установите зависимости:
```bash
source .venv/bin/activate
pip install -e .
```

### Engine расчёты неверны

Пересоберите Rust extension:
```bash
source .venv/bin/activate
maturin develop --release -m crates/ag-core/Cargo.toml
```
