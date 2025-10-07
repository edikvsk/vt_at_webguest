# Быстрый старт

## 1) Установка зависимостей
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

## 2) Запуск конкретного теста
```powershell
py -3 -m pytest test\smoke\stream_controls\test_start_stream.py -v
```

## 3) Запуск всех тестов
```powershell
py -3 -m pytest -v
```

### Проверка конфигурации
```powershell
py -3 -c "from utils.config_manager import config; config.print_config_summary()"
```

### Запуск по категориям (папки)
```powershell
py -3 -m pytest test\smoke\ -v
py -3 -m pytest test\regress\ -v
```

### Запуск с маркерами
```powershell
py -3 -m pytest -m smoke -v
py -3 -m pytest -m fast -v
```

### Полезные переменные окружения (пример)
```powershell
set BROWSER_HEADLESS=true
set TEST_DEFAULT_TIMEOUT=15
set TEST_RETRY_COUNT=5
set TEST_SCREENSHOT_ON_FAILURE=true
set LOG_LEVEL=DEBUG
```

Дополнительно:
- Активация окружения в новом терминале: `. .\.venv\Scripts\Activate.ps1`
- Все маркеры: `py -3 -m pytest --markers`
