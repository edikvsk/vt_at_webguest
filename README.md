# VT WebGuest Autotests

## Установка зависимостей и подготовка окружения

Рекомендуемый способ — автоматизированный скрипт для Windows PowerShell.

```powershell
# 1) Запустить из корня репозитория
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1

# 2) (опционально) Активировать окружение вручную в новых сессиях
. .\.venv\Scripts\Activate.ps1
```

Альтернативно вручную:
```powershell
py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Настройка конфигурации
Система конфигурации теперь управляется через `utils/config_manager.py` и поддерживает переменные окружения. Менять `utils/config.py` больше не требуется — он проксирует значения из менеджера конфигурации.

Минимальный набор переменных окружения (при необходимости переопределить значения по умолчанию):
```powershell
# Пути к Chrome и Chromedriver
set CHROME_DRIVER_PATH=C:\path\to\chromedriver.exe
set CHROME_BROWSER_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe

# Пути к VT Publisher
set VT_PROCESS_PATH=C:\path\to\VT_Publisher.exe
set VT_PUBLISHER_XML_PATH=C:\path\to\DLL\publisher.xml
set VT_CONFIG_INI_PATH=C:\path\to\repo\utils\config.ini

# Идентификаторы медиа-устройств
set VIDEO_DEVICE_ID=<video_device_id>
set AUDIO_DEVICE_ID=<audio_device_id>
set CAMERA_FOR_SELECTION=<camera name>
set MIC_FOR_SELECTION=<microphone name>
```

Как получить `VIDEO_DEVICE_ID` и `AUDIO_DEVICE_ID`:
1. Запустить WebGuest стрим
2. Открыть Chrome DevTools → Console и выполнить:
```js
navigator.mediaDevices.enumerateDevices()
  .then(devices => {
    devices.forEach(device => {
      if (device.kind === 'videoinput') {
        console.log('Video Device ID:', device.deviceId, 'Label:', device.label);
      } else if (device.kind === 'audioinput') {
        console.log('Audio Device ID:', device.deviceId, 'Label:', device.label);
      }
    });
  })
  .catch(err => console.error('Error accessing media devices.', err));
```

## Быстрая проверка конфигурации
```powershell
py -3 -c "from utils.config_manager import config; config.print_config_summary()"
```

## Запуск тестов (пример)
```powershell
py -3 -m pytest --collect-only -q
py -3 -m pytest test\smoke\stream_controls\test_start_stream.py -v
```