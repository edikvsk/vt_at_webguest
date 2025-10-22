# Настройка медиа-устройств

Подробное руководство по настройке камеры и микрофона для VT WebGuest Autotests.

## Автоматическое определение устройств

Система автоматически находит и настраивает медиа-устройства по частичному совпадению имени.

### Быстрая настройка

```powershell
# Указываем частичное имя устройства
$env:CAMERA_FOR_SELECTION = "Logi"
$env:MIC_FOR_SELECTION = "Logi"
```

### Как это работает

1. **Поиск устройств**: Система сканирует все доступные медиа-устройства через PowerShell/WMI
2. **Фильтрация по имени**: Ищет устройства, содержащие указанное имя (без учета регистра)
3. **Определение ID**: Генерирует уникальные ID для найденных устройств
4. **Настройка браузера**: Передает ID устройств в Chrome для автоматического выбора

### Примеры поиска

| Поисковый запрос | Найденные устройства |
|------------------|----------------------|
| `"Logi"` | Logitech C270 HD Webcam, Microphone (Logi C270 HD WebCam) |
| `"Camera"` | Logi USB Camera (C270 HD WebCam), Brother DCP-L8410CDW |
| `"USB"` | Logi USB Camera (C270 HD WebCam) |
| `"HD"` | Logi C270 HD WebCam, Microphone (Logi C270 HD WebCam) |

## Просмотр доступных устройств

### Команда для просмотра

```powershell
python scripts\test_devices.py
```

### Что показывает скрипт

- 📹 **Видеоустройства** - все доступные камеры
- 🎤 **Аудиоустройства** - все доступные микрофоны
- 🔍 **Результаты поиска** - какие устройства найдены по имени
- ⚙️ **Текущая конфигурация** - активные настройки

### Пример вывода

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
  2. Intel(R) Display Audio
     ID: a3a70ed3d975247013c05241f03e51...
```

## Быстрая настройка через скрипт

### PowerShell скрипт

```powershell
# Настройка по имени устройства
.\scripts\setup_devices.ps1 -CameraName "Logi" -MicName "Logi"

# Настройка с конкретными ID устройств
.\scripts\setup_devices.ps1 -VideoDeviceId "your_video_id" -AudioDeviceId "your_audio_id"
```

### Что делает скрипт

1. **Устанавливает переменные окружения** для текущей сессии
2. **Тестирует конфигурацию** - проверяет, что устройства найдены
3. **Показывает доступные устройства** - полный список
4. **Предлагает постоянное сохранение** - инструкции для профиля PowerShell

## Ручная настройка

### Если автоматический поиск не работает

```powershell
# Указываем конкретные ID устройств
$env:VIDEO_DEVICE_ID = "c7785e31c99ffb0717606da717f48b..."
$env:AUDIO_DEVICE_ID = "efb923c08da0f0d90100b1d9b791b6..."
```

### Как получить ID устройств

#### Метод 1: Через браузер

1. Запустите WebGuest стрим
2. Откройте Chrome DevTools (F12)
3. Перейдите в Console
4. Выполните команду:

```javascript
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

#### Метод 2: Через PowerShell

```powershell
# Получить список видеоустройств
Get-WmiObject -Class Win32_PnPEntity | Where-Object {
    $_.PNPClass -eq 'Camera' -or $_.Name -like '*camera*'
} | Select-Object Name, DeviceID

# Получить список аудиоустройств
Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, DeviceID
```

## Постоянное сохранение настроек

### В профиле PowerShell

```powershell
# Добавить в профиль PowerShell
[Environment]::SetEnvironmentVariable('CAMERA_FOR_SELECTION', 'Logi', 'User')
[Environment]::SetEnvironmentVariable('MIC_FOR_SELECTION', 'Logi', 'User')
```

### Через файл .env

Создайте файл `.env` в корне проекта:

```env
CAMERA_FOR_SELECTION=Logi
MIC_FOR_SELECTION=Logi
```

## Решение проблем

### Устройство не найдено

**Проблема**: `"Устройство с именем 'Logi' не найдено"`

**Решения**:
1. Проверьте правильность имени устройства
2. Убедитесь, что устройство подключено и работает
3. Попробуйте более общий поиск: `"Camera"`, `"USB"`, `"HD"`
4. Используйте ручную настройку с конкретными ID

### Ошибка "Overconstrained error"

**Проблема**: `"Overconstrained error cannot be applied to unknown camera"`

**Решение**: Система автоматически переключается на fake устройства для стабильной работы тестов.

### Устройство найдено, но не работает

**Проблема**: Устройство найдено, но WebRTC стрим не запускается

**Решения**:
1. Проверьте права доступа к устройству
2. Убедитесь, что устройство не используется другим приложением
3. Перезапустите браузер
4. Проверьте логи Chrome DevTools

## Логирование и отладка

### Включение подробных логов

```powershell
$env:SHOW_CONFIG_SUMMARY = "true"
```

### Просмотр логов устройства

```powershell
python scripts\test_devices.py
```

### Логи в Chrome DevTools

Откройте DevTools → Console для просмотра:
- Список доступных устройств
- Процесс поиска устройств по имени
- Ошибки доступа к медиа-устройствам

## Лучшие практики

1. **Используйте частичные имена** - более гибкий поиск
2. **Тестируйте настройки** - всегда проверяйте через `test_devices.py`
3. **Сохраняйте настройки** - используйте профиль PowerShell или .env файл
4. **Мониторьте логи** - следите за сообщениями о найденных устройствах
5. **Имейте резервный план** - знайте, как переключиться на ручную настройку
