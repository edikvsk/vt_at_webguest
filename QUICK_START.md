# Быстрый старт

1) Установка всего (venv, зависимости, Chrome Beta + Chromedriver)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

2) Запуск конкретного теста
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\stream_controls\test_start_stream.py -v
```

Дополнительно:
```powershell
# Запуск всех тестов
py -3 -m pytest -v

# Проверка конфигурации
py -3 -c "from utils.config_manager import config; config.print_config_summary()"

# Запуск по категориям (папки)
py -3 -m pytest test\smoke\ -v
py -3 -m pytest test\regress\ -v

# Запуск с маркерами
py -3 -m pytest -m smoke -v
py -3 -m pytest -m fast -v

# Полезные переменные окружения (пример)
$env:BROWSER_HEADLESS = "true"
$env:TEST_DEFAULT_TIMEOUT = "15"
$env:TEST_RETRY_COUNT = "5"
$env:TEST_SCREENSHOT_ON_FAILURE = "true"
$env:LOG_LEVEL = "DEBUG"

# Активация окружения в новом терминале
. .\.venv\Scripts\Activate.ps1

# Все маркеры
py -3 -m pytest --markers
```
