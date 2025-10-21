# Скрипты и утилиты

## Основные скрипты

### `scripts/setup.ps1`
Установка всех зависимостей проекта:
- Создание виртуального окружения
- Установка Python пакетов
- Скачивание Chrome Beta и ChromeDriver
- Настройка окружения

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

### `scripts/run.ps1`
Запуск тестов:
```powershell
# Запуск одного теста
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\stream_controls\test_start_stream.py -v

# Запуск всех тестов
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\ -v
```

### `scripts/detect_media_devices.py`
Управление медиа-устройствами:

```powershell
# Показать все доступные устройства
python scripts/detect_media_devices.py --list

# Автоматически найти и настроить устройства
python scripts/detect_media_devices.py --auto-detect

# Найти устройства по названию
python scripts/detect_media_devices.py --camera "Logi" --mic "Logi"

# Обновить конфигурацию найденными устройствами
python scripts/detect_media_devices.py --camera "Logi" --mic "Logi" --update-config

# Показать текущую конфигурацию
python scripts/detect_media_devices.py --show-config
```

## Тестовые скрипты

### `test_media_detection.py`
Тестирование функционала автоматического определения медиа-устройств:
```powershell
python test_media_detection.py
```

### `utils/stable_media_config.py`
Тестирование стабильной конфигурации медиа-устройств:
```powershell
python utils/stable_media_config.py
```

## Утилиты

### `utils/config_manager.py`
Менеджер конфигурации с поддержкой:
- Автоматического определения путей
- Переменных окружения
- Валидации конфигурации
- Динамического определения медиа-устройств

### `utils/media_device_detector.py`
Детектор медиа-устройств:
- Поиск доступных камер и микрофонов
- Получение ID устройств
- Поиск по названию

### `utils/stable_media_config.py`
Стабильная конфигурация медиа-устройств:
- Работа с названиями устройств вместо ID
- Кэширование результатов
- Динамическое формирование media_constraints

## Примеры использования

### Быстрая настройка медиа-устройств:
```powershell
# 1. Показать доступные устройства
python scripts/detect_media_devices.py --list

# 2. Найти и настроить устройства Logitech
python scripts/detect_media_devices.py --camera "Logi" --mic "Logi" --update-config

# 3. Проверить конфигурацию
python scripts/detect_media_devices.py --show-config
```

### Тестирование конфигурации:
```powershell
# 1. Тест общего функционала
python test_media_detection.py

# 2. Тест стабильной конфигурации
python utils/stable_media_config.py

# 3. Проверка конфигурации
py -3 -c "from utils.config_manager import config; config.print_config_summary()"
```

### Запуск тестов:
```powershell
# 1. Активировать окружение
. .\.venv\Scripts\Activate.ps1

# 2. Запустить тесты
python -m pytest test/smoke/stream_controls/test_start_stream.py -v

# 3. Или через скрипт
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\stream_controls\test_start_stream.py -v
```

## Отладка

### Проверка путей:
```powershell
py -3 -c "from utils.config_manager import config; print('Chrome:', config.browser.chrome_browser_path); print('Driver:', config.browser.chrome_driver_path)"
```

### Проверка медиа-устройств:
```powershell
py -3 -c "from utils.config_manager import config; config.print_available_media_devices()"
```

### Проверка media_constraints:
```powershell
py -3 -c "from utils.config_manager import config; print('Constraints:', config.get_media_constraints())"
```
