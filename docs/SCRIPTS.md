# Скрипты и утилиты

Описание всех доступных скриптов и утилит для VT WebGuest Autotests.

## Основные скрипты

### setup.ps1

**Назначение**: Полная установка проекта с зависимостями

**Использование**:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

**Что делает**:
- Создает виртуальное окружение Python
- Устанавливает зависимости из requirements.txt
- Скачивает и устанавливает Chrome for Testing (Beta)
- Скачивает и устанавливает ChromeDriver
- Настраивает пути и переменные окружения

**Результат**:
- Готовое к работе окружение в папке `.venv`
- Chrome и ChromeDriver в папке `.tools`
- Все зависимости установлены

### run.ps1

**Назначение**: Запуск тестов с настройками

**Использование**:
```powershell
# Один тест
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\stream_controls\test_start_stream.py -v

# Все тесты
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\ -v

# Конкретная папка
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\ -v
```

**Параметры**:
- `-TestPath` - путь к тесту или папке с тестами
- `-v` - подробный вывод (verbose)
- `-s` - показывать print() в тестах
- `--tb=short` - короткий traceback при ошибках

**Что делает**:
- Активирует виртуальное окружение
- Запускает pytest с указанными параметрами
- Обрабатывает ошибки и выводит результаты

### install_chrome_beta.ps1

**Назначение**: Установка Chrome for Testing (Beta)

**Использование**:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_chrome_beta.ps1
```

**Что делает**:
- Определяет последнюю версию Chrome Beta
- Скачивает архив Chrome for Testing
- Распаковывает в папку `.tools/chrome-Beta/`
- Скачивает соответствующий ChromeDriver
- Распаковывает ChromeDriver в `.tools/chromedriver-Beta/`

## Утилиты для медиа-устройств

### test_devices.py

**Назначение**: Тестирование и просмотр медиа-устройств

**Использование**:
```powershell
python scripts\test_devices.py
```

**Что показывает**:
- 📹 Список всех видеоустройств
- 🎤 Список всех аудиоустройств
- 🔍 Результаты поиска по именам
- ⚙️ Текущую конфигурацию
- 🧪 Тестирование поиска с разными именами

**Пример вывода**:
```
============================================================
ДОСТУПНЫЕ МЕДИА-УСТРОЙСТВА
============================================================

📹 ВИДЕОУСТРОЙСТВА (7):
  1. Logi USB Camera (C270 HD WebCam)
     ID: c7785e31c99ffb0717606da717f48b...
  2. Logi C270 HD WebCam
     ID: b8b55f5a1bcd502c3c98debc9527a1...

🎤 АУДИОУСТРОЙСТВА (38):
  1. Microphone (Logi C270 HD WebCam)
     ID: efb923c08da0f0d90100b1d9b791b6...
```

### setup_devices.ps1

**Назначение**: Быстрая настройка медиа-устройств

**Использование**:
```powershell
# Настройка по имени устройства
.\scripts\setup_devices.ps1 -CameraName "Logi" -MicName "Logi"

# Настройка с конкретными ID
.\scripts\setup_devices.ps1 -VideoDeviceId "your_video_id" -AudioDeviceId "your_audio_id"
```

**Параметры**:
- `-CameraName` - имя камеры для поиска
- `-MicName` - имя микрофона для поиска
- `-VideoDeviceId` - конкретный ID видеоустройства
- `-AudioDeviceId` - конкретный ID аудиоустройства

**Что делает**:
- Устанавливает переменные окружения для текущей сессии
- Тестирует конфигурацию через `test_devices.py`
- Показывает доступные устройства
- Предлагает инструкции для постоянного сохранения

## Утилиты конфигурации

### Проверка конфигурации

**Команда**:
```powershell
py -3 -c "from utils.config_manager import config; config.print_config_summary()"
```

**Что показывает**:
- 📁 Пути к Chrome, ChromeDriver, VT Publisher
- 🎥 Настройки медиа-устройств
- ⚙️ Параметры тестов
- 🌐 Настройки браузера

### Проверка медиа-устройств

**Команда**:
```powershell
python scripts\test_devices.py
```

**Что показывает**:
- Список всех доступных устройств
- Результаты поиска по текущим настройкам
- Тестирование с разными именами устройств

## Примеры использования

### Полная установка проекта

```powershell
# 1. Установка всех зависимостей
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1

# 2. Настройка устройств
.\scripts\setup_devices.ps1 -CameraName "Logi" -MicName "Logi"

# 3. Проверка конфигурации
py -3 -c "from utils.config_manager import config; config.print_config_summary()"

# 4. Запуск тестов
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\stream_controls\test_start_stream.py -v
```

### Отладка проблем с устройствами

```powershell
# 1. Просмотр всех устройств
python scripts\test_devices.py

# 2. Тестирование разных имен
$env:CAMERA_FOR_SELECTION = "Camera"
$env:MIC_FOR_SELECTION = "Microphone"
python scripts\test_devices.py

# 3. Проверка конфигурации
py -3 -c "from utils.config_manager import config; config.print_config_summary()"
```

### Запуск разных наборов тестов

```powershell
# Smoke тесты
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\ -v

# Regression тесты
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\regress\ -v

# Конкретный тест
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\stream_controls\test_start_stream.py -v
```

## Структура скриптов

```
scripts/
├── setup.ps1                    # Основная установка
├── run.ps1                      # Запуск тестов
├── install_chrome_beta.ps1      # Установка Chrome
├── setup_devices.ps1           # Настройка устройств
└── test_devices.py             # Тестирование устройств
```

## Создание собственных скриптов

### PowerShell скрипт для настройки окружения

```powershell
# setup_environment.ps1
param(
    [string]$CameraName = "Logi",
    [string]$MicName = "Logi",
    [string]$BrowserWidth = "1920",
    [string]$BrowserHeight = "1080"
)

Write-Host "Настройка окружения VT WebGuest Autotests" -ForegroundColor Cyan

# Установка переменных окружения
$env:CAMERA_FOR_SELECTION = $CameraName
$env:MIC_FOR_SELECTION = $MicName
$env:BROWSER_WINDOW_WIDTH = $BrowserWidth
$env:BROWSER_WINDOW_HEIGHT = $BrowserHeight

# Проверка конфигурации
Write-Host "Проверка конфигурации..." -ForegroundColor Yellow
py -3 -c "from utils.config_manager import config; config.print_config_summary()"

Write-Host "Окружение настроено!" -ForegroundColor Green
```

### Python скрипт для массового тестирования

```python
# mass_test.py
import subprocess
import sys
import os

def run_test(test_path):
    """Запускает тест и возвращает результат"""
    cmd = [
        "powershell", "-ExecutionPolicy", "Bypass", 
        "-File", "scripts\\run.ps1", 
        "-TestPath", test_path, "-v"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def main():
    """Запускает все smoke тесты"""
    test_dirs = [
        "test\\smoke\\stream_controls",
        "test\\smoke\\stream_stats", 
        "test\\smoke\\url_settings"
    ]
    
    for test_dir in test_dirs:
        print(f"Запуск тестов в {test_dir}...")
        success = run_test(test_dir)
        status = "✅ УСПЕХ" if success else "❌ ОШИБКА"
        print(f"{status}: {test_dir}")

if __name__ == "__main__":
    main()
```

## Решение проблем со скриптами

### Ошибка "ExecutionPolicy"

**Проблема**: `ExecutionPolicy` запрещает выполнение скриптов

**Решение**:
```powershell
# Временно разрешить выполнение
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Или использовать параметр
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

### Ошибка "Python не найден"

**Проблема**: `Python was not found`

**Решение**:
```powershell
# Использовать py вместо python
py -3 scripts\test_devices.py

# Или активировать виртуальное окружение
. .\.venv\Scripts\Activate.ps1
python scripts\test_devices.py
```

### Ошибка "Chrome не найден"

**Проблема**: Chrome не установлен или не найден

**Решение**:
```powershell
# Переустановить Chrome
powershell -ExecutionPolicy Bypass -File .\scripts\install_chrome_beta.ps1

# Или указать путь вручную
$env:CHROME_BROWSER_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

## Лучшие практики

1. **Всегда используйте полные пути** к скриптам
2. **Проверяйте ExecutionPolicy** перед запуском PowerShell скриптов
3. **Активируйте виртуальное окружение** перед запуском Python скриптов
4. **Тестируйте скрипты** на простых примерах перед массовым использованием
5. **Мониторьте логи** для выявления проблем
6. **Используйте параметры** для гибкой настройки скриптов
