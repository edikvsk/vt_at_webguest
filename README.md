# VT WebGuest Autotests

Автотесты для VT WebGuest с поддержкой автоматического определения медиа-устройств.

## Быстрый старт

### 1. Установка
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

### 2. Настройка медиа-устройств
```powershell
# Указываем частичное имя устройства (например, "Logi" найдет "Logitech C270 HD Webcam")
$env:CAMERA_FOR_SELECTION = "Logi"
$env:MIC_FOR_SELECTION = "Logi"
```

Система автоматически:
- Найдет устройство по частичному совпадению имени
- Определит его уникальный ID
- Настроит Chrome для использования именно этого устройства

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
- **[Отладка и логирование](docs/DEBUGGING.md)** - решение проблем и анализ логов

## Основные возможности

- ✅ **Автоматическое определение медиа-устройств** - система сама находит камеру и микрофон
- ✅ **Динамическая конфигурация** - устройства определяются при каждом запуске
- ✅ **Автоматическая установка зависимостей** - Chrome, ChromeDriver, VT Publisher
- ✅ **Гибкая настройка** - через переменные окружения или автоматически
- ✅ **Подробное логирование** - для отладки и мониторинга

## Проверка работы

```powershell
# Проверить конфигурацию
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

## Требования

- Windows 10/11
- Python 3.8+
- PowerShell 5.0+
- Доступ к интернету (для скачивания зависимостей)
- Доступ к \192.168.10.100
- 2 Гб. свободного места на диске