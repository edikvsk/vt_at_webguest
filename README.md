# VT WebGuest Autotests

## Test Bot integration

The Test Bot prepares this repository with the self-contained environment
bootstrap:

```powershell
powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass `
  -File .\scripts\ensure_environment.ps1
```

For Video Transport, `run=all project=vt` runs both the VT wrapper tests and
all WebGuest pytest tests. Use `type=webguest` to run only this repository.

Every collected pytest node ID must contain a `VT####` YouTrack identity.
Smoke tests that do not belong to another issue must use `VT1626` in both the
test file and test function name. The Test Bot rejects unnumbered nodes during
discovery.

Автотесты для VT WebGuest с поддержкой автоматического определения медиа-устройств и конфигурации по машинам.

## Быстрый старт

### 1. Установка зависимостей
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

### 2. Настройка медиа-устройств
Система автоматически определяет машину и загружает конфигурацию с `\\web\VT_WebGuest_config\appconfig.json`

- **EDWARD** - использует устройства "Logi" (Logitech)  
- **DEMOSTAND** - использует устройства "A4"
- **DEFAULT** - для всех остальных машин используются устройства "A4"

### 3. Запуск тестов
```powershell
# Один тест
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\stream_controls\test_start_stream.py -v

# Все тесты
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\ -v
```

## Документация

- **[Настройка медиа-устройств](docs/MEDIA_DEVICES.md)** - подробное руководство по настройке камеры и микрофона
- **[Конфигурация](docs/CONFIGURATION.md)** - все переменные окружения и настройки
- **[Скрипты и утилиты](docs/SCRIPTS.md)** - описание всех доступных скриптов
- **[Архитектура проекта](docs/ARCHITECTURE.md)** - структура кода и принципы работы


## Проверка работы

```powershell
# Проверить конфигурацию и определение машины
py -3 -c "from utils.config_manager import config; config.print_config_summary()"

# Проверить медиа-устройства
python scripts\test_devices.py
```

## Структура проекта

```
vt_at_webguest/
├── docs/                    # Документация
├── scripts/                 # Скрипты установки и запуска
├── test/                    # Тесты
├── utils/                   # Утилиты и конфигурация
├── pages/                   # Page Object Model
└── logs/                    # Логи тестов
```

## Конфигурация машин

Система автоматически определяет машину и загружает конфигурацию с `\\192.168.10.100\web\VT_WebGuest_config\appconfig.json`

## Требования

- Windows 10/11
- Python 3.8+
- PowerShell 5.0+
- Доступ к интернету (для скачивания зависимостей)
- Доступ к \192.168.10.100
- 2 Гб. свободного места на диске
