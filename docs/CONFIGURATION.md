# Конфигурация проекта

## Переменные окружения

### Основные настройки
```powershell
# Автоматическое определение медиа-устройств
$env:AUTO_DETECT_MEDIA_DEVICES = "true"
$env:USE_DYNAMIC_MEDIA_DETECTION = "true"

# Названия устройств для поиска
$env:CAMERA_FOR_SELECTION = "Logi"
$env:MIC_FOR_SELECTION = "Logi"

# ID устройств (если не используется автоматическое определение)
$env:VIDEO_DEVICE_ID = "<video_device_id>"
$env:AUDIO_DEVICE_ID = "<audio_device_id>"
```

### Настройки браузера
```powershell
# Пути к Chrome (автоматически определяются из .tools)
$env:CHROME_BROWSER_PATH = "C:/path/to/chrome.exe"
$env:CHROME_DRIVER_PATH = "C:/path/to/chromedriver.exe"

# Настройки окна браузера
$env:BROWSER_WINDOW_WIDTH = "1920"
$env:BROWSER_WINDOW_HEIGHT = "1080"
$env:BROWSER_HEADLESS = "false"
```

### Настройки VT
```powershell
# Пути к VT (автоматически определяются)
$env:VT_PROCESS_PATH = "C:/path/to/VT_Publisher.exe"
$env:VT_PROCESS_NAME = "VT_Publisher.exe"
$env:VT_PUBLISHER_XML_PATH = "C:/path/to/publisher.xml"
$env:VT_CONFIG_INI_PATH = "C:/path/to/config.ini"
$env:VT_SOURCE_TO_PUBLISHING = "Screen:"
$env:VT_PRIVATE_JSON_PATH = "C:/path/to/private.json"
```

### Настройки тестов
```powershell
# Таймауты
$env:TEST_DEFAULT_TIMEOUT = "10"
$env:TEST_LONG_TIMEOUT = "30"
$env:TEST_SHORT_TIMEOUT = "5"

# Повторы
$env:TEST_RETRY_COUNT = "3"
$env:TEST_RETRY_DELAY = "1.0"

# Дополнительные настройки
$env:TEST_SCREENSHOT_ON_FAILURE = "true"
$env:TEST_VIDEO_RECORDING = "false"
```

## Проверка конфигурации

### Показать сводку конфигурации:
```powershell
py -3 -c "from utils.config_manager import config; config.print_config_summary()"
```

### Показать доступные медиа-устройства:
```powershell
python scripts/detect_media_devices.py --list
```

### Показать текущую конфигурацию медиа-устройств:
```powershell
python scripts/detect_media_devices.py --show-config
```

## Автоматическое определение путей

Проект автоматически определяет пути к:
- Chrome браузеру и ChromeDriver (из папки `.tools`)
- VT Publisher (скачивает последнюю версию при необходимости)
- Конфигурационным файлам

Если автоматическое определение не работает, можно задать пути вручную через переменные окружения.

## Приоритет настроек

1. **Переменные окружения** - высший приоритет
2. **Автоматическое определение** - средний приоритет
3. **Значения по умолчанию** - низший приоритет

## Пример полной конфигурации

```powershell
# Медиа-устройства
$env:USE_DYNAMIC_MEDIA_DETECTION = "true"
$env:CAMERA_FOR_SELECTION = "Logi"
$env:MIC_FOR_SELECTION = "Logi"

# Браузер
$env:BROWSER_HEADLESS = "false"
$env:BROWSER_WINDOW_WIDTH = "1920"
$env:BROWSER_WINDOW_HEIGHT = "1080"

# Тесты
$env:TEST_DEFAULT_TIMEOUT = "15"
$env:TEST_RETRY_COUNT = "5"
$env:TEST_SCREENSHOT_ON_FAILURE = "true"

# Показать сводку
py -3 -c "from utils.config_manager import config; config.print_config_summary()"
```
