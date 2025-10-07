# VT WebGuest Autotests

## Quick Start (Windows PowerShell)

1) Установка всего необходимого (виртуальное окружение, зависимости, Chrome Beta + Chromedriver)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

2) Запуск одного теста (Chrome Beta подхватится автоматически)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\stream_controls\test_start_stream.py -v
```

Дополнительно (при необходимости):
- Активировать окружение вручную в новой сессии
```powershell
. .\.venv\Scripts\Activate.ps1
```

## Альтернативная ручная установка (без setup.ps1)
```powershell
py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Chrome for Testing (Beta) и Chromedriver устанавливаются автоматически в `setup.ps1`. Проект сам находит их в каталоге `.tools` — ничего дополнительно подключать не нужно.

## Настройка параметров окружения (опционально)
Система конфигурации управляется через `utils/config_manager.py`. Значения можно переопределять переменными окружения при необходимости:
```powershell
# Пути к VT Publisher (обязательно указать под вашу машину)
$env:VT_PROCESS_PATH = "C:\Path\To\VT\VT_Publisher.exe"
$env:VT_PUBLISHER_XML_PATH = "C:\Path\To\VT\DLL\publisher.xml"
$env:VT_CONFIG_INI_PATH = "$PWD\utils\config.ini"

# Идентификаторы медиа-устройств
$env:VIDEO_DEVICE_ID = "<video_device_id>"
$env:AUDIO_DEVICE_ID = "<audio_device_id>"
$env:CAMERA_FOR_SELECTION = "<camera name>"
$env:MIC_FOR_SELECTION = "<microphone name>"
```
Пути к Chrome/Chromedriver задавать не требуется: проект автоматически использует установки из `.tools`. При желании можно переопределить через `$env:CHROME_BROWSER_PATH` и `$env:CHROME_DRIVER_PATH`.

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

## Проверка конфигурации (опционально)
```powershell
py -3 -c "from utils.config_manager import config; config.print_config_summary()"
```

## Запуск тестов
```powershell
py -3 -m pytest --collect-only -q
py -3 -m pytest test\smoke\stream_controls\test_start_stream.py -v
```

Либо коротко через скрипт:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\stream_controls\test_start_stream.py -v
```