# Конфигурация

Полное руководство по настройке VT WebGuest Autotests через переменные окружения.

## Переменные окружения

### Медиа-устройства

| Переменная | Описание | Пример | По умолчанию |
|------------|----------|--------|--------------|
| `CAMERA_FOR_SELECTION` | Имя камеры для поиска | `"Logi"` | `"Logi"` |
| `MIC_FOR_SELECTION` | Имя микрофона для поиска | `"Logi"` | `"Logi"` |
| `VIDEO_DEVICE_ID` | Конкретный ID видеоустройства | `"c7785e31c99ffb..."` | Автоопределение |
| `AUDIO_DEVICE_ID` | Конкретный ID аудиоустройства | `"efb923c08da0f0..."` | Автоопределение |

### Браузер

| Переменная | Описание | Пример | По умолчанию |
|------------|----------|--------|--------------|
| `CHROME_BROWSER_PATH` | Путь к Chrome | `"C:\Program Files\Google\Chrome\Application\chrome.exe"` | Автопоиск в `.tools` |
| `CHROME_DRIVER_PATH` | Путь к ChromeDriver | `"C:\chromedriver\chromedriver.exe"` | Автопоиск в `.tools` |
| `BROWSER_WINDOW_WIDTH` | Ширина окна браузера | `1920` | `1920` |
| `BROWSER_WINDOW_HEIGHT` | Высота окна браузера | `1080` | `1080` |
| `BROWSER_HEADLESS` | Запуск в headless режиме | `true`/`false` | `false` |

### VT Publisher

| Переменная | Описание | Пример | По умолчанию |
|------------|----------|--------|--------------|
| `VT_PROCESS_PATH` | Путь к VT_Publisher.exe | `"C:\VT\VT_Publisher.exe"` | Автозагрузка |
| `VT_PROCESS_NAME` | Имя процесса VT | `"VT_Publisher.exe"` | `"VT_Publisher.exe"` |
| `VT_PUBLISHER_XML_PATH` | Путь к publisher.xml | `"C:\VT\DLL\publisher.xml"` | Автозагрузка |
| `VT_CONFIG_INI_PATH` | Путь к config.ini | `"utils\config.ini"` | `"utils\config.ini"` |
| `VT_SOURCE_TO_PUBLISHING` | Источник для публикации | `"Screen:"` | `"Screen:"` |
| `VT_PRIVATE_JSON_PATH` | Путь к private.json | `"\\\\server\share\file.json"` | Сетевая папка |

### Настройки тестов

| Переменная | Описание | Пример | По умолчанию |
|------------|----------|--------|--------------|
| `TEST_DEFAULT_TIMEOUT` | Таймаут по умолчанию (сек) | `10` | `10` |
| `TEST_LONG_TIMEOUT` | Длинный таймаут (сек) | `30` | `30` |
| `TEST_SHORT_TIMEOUT` | Короткий таймаут (сек) | `5` | `5` |
| `TEST_RETRY_COUNT` | Количество повторов | `3` | `3` |
| `TEST_RETRY_DELAY` | Задержка между повторами (сек) | `1.0` | `1.0` |
| `TEST_SCREENSHOT_ON_FAILURE` | Скриншоты при ошибках | `true`/`false` | `true` |
| `TEST_VIDEO_RECORDING` | Запись видео тестов | `true`/`false` | `false` |

### Отладка

| Переменная | Описание | Пример | По умолчанию |
|------------|----------|--------|--------------|
| `SHOW_CONFIG_SUMMARY` | Показывать сводку конфигурации | `true`/`false` | `false` |

## Примеры конфигурации

### Базовая настройка

```powershell
# Медиа-устройства
$env:CAMERA_FOR_SELECTION = "Logi"
$env:MIC_FOR_SELECTION = "Logi"

# Браузер
$env:BROWSER_WINDOW_WIDTH = 1920
$env:BROWSER_WINDOW_HEIGHT = 1080
$env:BROWSER_HEADLESS = $false

# Тесты
$env:TEST_DEFAULT_TIMEOUT = 10
$env:TEST_SCREENSHOT_ON_FAILURE = $true
```

### Продвинутая настройка

```powershell
# Конкретные устройства
$env:VIDEO_DEVICE_ID = "c7785e31c99ffb0717606da717f48b..."
$env:AUDIO_DEVICE_ID = "efb923c08da0f0d90100b1d9b791b6..."

# Кастомные пути
$env:CHROME_BROWSER_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$env:CHROME_DRIVER_PATH = "C:\chromedriver\chromedriver.exe"

# VT Publisher
$env:VT_PROCESS_PATH = "C:\VT\Video Transport 1.9.5.1204(x64)\VT_Publisher.exe"
$env:VT_PUBLISHER_XML_PATH = "C:\VT\Video Transport 1.9.5.1204(x64)\DLL\publisher.xml"

# Отладка
$env:SHOW_CONFIG_SUMMARY = "true"
```

### Headless режим

```powershell
# Запуск без GUI
$env:BROWSER_HEADLESS = $true
$env:TEST_SCREENSHOT_ON_FAILURE = $true
$env:TEST_VIDEO_RECORDING = $true
```

## Автоматическая конфигурация

### Автопоиск Chrome и ChromeDriver

Система автоматически ищет Chrome и ChromeDriver в папке `.tools`:

```
.tools/
├── chrome-Beta/
│   └── chrome-win64/
│       └── chrome.exe
└── chromedriver-Beta/
    └── chromedriver-win64/
        └── chromedriver.exe
```

### Автозагрузка VT Publisher

Система автоматически:
1. Определяет последнюю версию VT с сервера releases.medialooks.net
2. Скачивает и распаковывает архив
3. Настраивает пути к VT_Publisher.exe и publisher.xml

### Автоопределение медиа-устройств

Система автоматически:
1. Сканирует доступные медиа-устройства через PowerShell/WMI
2. Ищет устройства по частичному совпадению имени
3. Генерирует уникальные ID устройств
4. Настраивает Chrome для использования найденных устройств

## Проверка конфигурации

### Команда проверки

```powershell
py -3 -c "from utils.config_manager import config; config.print_config_summary()"
```

### Пример вывода

```
==================================================
СВОДКА КОНФИГУРАЦИИ
==================================================

📁 ПУТИ:
  Chrome Driver: C:\Users\edwar\vt-at-test\vt_at_webguest\.tools\chromedriver-Beta\chromedriver-win64\chromedriver.exe
  Chrome Browser: C:\Users\edwar\vt-at-test\vt_at_webguest\.tools\chrome-Beta\chrome-win64\chrome.exe
  VT Process: C:\Users\edwar\vt-at-test\vt_at_webguest\.tools\VT\1.9.5.1204\Video Transport 1.9.5.1204(x64)\VT_Publisher.exe
  Config INI: C:\Users\edwar\vt-at-test\vt_at_webguest\utils\config.ini

🎥 МЕДИА-УСТРОЙСТВА:
  Video Device ID: c7785e31c99ffb071760...
  Audio Device ID: efb923c08da0f0d90100...
  Camera: Logi
  Microphone: Logi

⚙️ НАСТРОЙКИ ТЕСТОВ:
  Default Timeout: 10с
  Long Timeout: 30с
  Retry Count: 3
  Screenshots: Включены

🌐 БРАУЗЕР:
  Размер окна: 1920x1080
  Headless: Отключен
==================================================
```

## Файлы конфигурации

### config.ini

Основной файл конфигурации:

```ini
[DEFAULT]
web_guest_page_url = https://vt08.medialooks.com:8080/wg2/dyiWmWYPZxfMHuMI
```

### .env файл

Создайте файл `.env` в корне проекта для постоянных настроек:

```env
# Медиа-устройства
CAMERA_FOR_SELECTION=Logi
MIC_FOR_SELECTION=Logi

# Браузер
BROWSER_WINDOW_WIDTH=1920
BROWSER_WINDOW_HEIGHT=1080
BROWSER_HEADLESS=false

# Тесты
TEST_DEFAULT_TIMEOUT=10
TEST_SCREENSHOT_ON_FAILURE=true

# Отладка
SHOW_CONFIG_SUMMARY=true
```

## Приоритет настроек

Настройки применяются в следующем порядке (от высшего к низшему приоритету):

1. **Переменные окружения** - имеют наивысший приоритет
2. **Автоматическое определение** - используется, если переменные не заданы
3. **Значения по умолчанию** - используются в крайнем случае

## Решение проблем конфигурации

### Ошибка "Конфигурация содержит ошибки"

**Причины**:
- Неверные пути к файлам
- Отсутствующие устройства
- Неправильные значения переменных

**Решение**:
1. Проверьте все пути к файлам
2. Убедитесь, что устройства подключены
3. Используйте `config.print_config_summary()` для диагностики

### Устройства не найдены

**Причины**:
- Неправильные имена устройств
- Устройства не подключены
- Проблемы с правами доступа

**Решение**:
1. Используйте `python scripts\test_devices.py` для проверки
2. Попробуйте более общие имена: `"Camera"`, `"USB"`
3. Используйте ручную настройку с конкретными ID

### Chrome не запускается

**Причины**:
- Неверный путь к Chrome
- Отсутствует ChromeDriver
- Конфликт версий

**Решение**:
1. Проверьте пути в конфигурации
2. Переустановите Chrome и ChromeDriver через `setup.ps1`
3. Используйте автопоиск в `.tools`

## Лучшие практики

1. **Используйте переменные окружения** для гибкой настройки
2. **Проверяйте конфигурацию** перед запуском тестов
3. **Сохраняйте настройки** в профиле PowerShell или .env файле
4. **Мониторьте логи** для выявления проблем
5. **Тестируйте изменения** на простых тестах перед массовым запуском
