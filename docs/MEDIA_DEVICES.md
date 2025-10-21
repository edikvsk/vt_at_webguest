# Настройка медиа-устройств

## Автоматическое определение (рекомендуется)

Проект поддерживает автоматическое определение медиа-устройств! 

### Быстрая настройка:
```powershell
# Показать все доступные устройства
python scripts/detect_media_devices.py --list

# Автоматически найти и настроить устройства
python scripts/detect_media_devices.py --auto-detect

# Найти устройства по названию (например, Logitech)
python scripts/detect_media_devices.py --camera "Logi" --mic "Logi" --update-config
```

### Включение автоматического определения:
```powershell
# Статическое определение (один раз при запуске)
$env:AUTO_DETECT_MEDIA_DEVICES = "true"
$env:CAMERA_FOR_SELECTION = "Logi"  # Название камеры (частичное совпадение)
$env:MIC_FOR_SELECTION = "Logi"     # Название микрофона (частичное совпадение)

# Динамическое определение (каждый раз при создании браузера)
$env:USE_DYNAMIC_MEDIA_DETECTION = "true"
$env:CAMERA_FOR_SELECTION = "Logi"
$env:MIC_FOR_SELECTION = "Logi"
```

### Рекомендуемый подход:
Используйте **динанамическое определение** (`USE_DYNAMIC_MEDIA_DETECTION = "true"`) - это гарантирует, что всегда будет выбрана правильная камера "Logi", даже если ID устройств изменятся.

## Ручная настройка (если нужно)

Если автоматическое определение не работает, можно настроить вручную:

```powershell
$env:VIDEO_DEVICE_ID = "<video_device_id>"
$env:AUDIO_DEVICE_ID = "<audio_device_id>"
$env:CAMERA_FOR_SELECTION = "<camera name>"
$env:MIC_FOR_SELECTION = "<microphone name>"
```

### Как получить ID устройств вручную:
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

## Дополнительные команды

### Просмотр доступных медиа-устройств:
```powershell
python scripts/detect_media_devices.py --list
```

### Показать текущую конфигурацию медиа-устройств:
```powershell
python scripts/detect_media_devices.py --show-config
```

### Автоматическое определение и обновление:
```powershell
python scripts/detect_media_devices.py --auto-detect
```

### Поиск устройств по названию:
```powershell
# Найти устройства Logitech
python scripts/detect_media_devices.py --camera "Logi" --mic "Logi"

# Найти устройства Microsoft
python scripts/detect_media_devices.py --camera "Microsoft" --mic "Microsoft"
```

### Тестирование стабильной конфигурации:
```powershell
# Тест стабильной конфигурации медиа-устройств
python utils/stable_media_config.py

# Тест общего функционала
python test_media_detection.py
```

### Проверка работы с динамическим определением:
```powershell
# Установить динамическое определение
$env:USE_DYNAMIC_MEDIA_DETECTION = "true"
$env:CAMERA_FOR_SELECTION = "Logi"
$env:MIC_FOR_SELECTION = "Logi"

# Проверить конфигурацию
py -3 -c "from utils.config_manager import config; print('Media constraints:', config.get_media_constraints())"
```

## Устранение неполадок

### Проблема: "MediaDevices API not supported"
**Решение:** Убедитесь, что Chrome запускается с правильными флагами. Система автоматически добавляет необходимые флаги.

### Проблема: "Не найдено устройство с названием"
**Решение:** 
1. Проверьте список доступных устройств: `python scripts/detect_media_devices.py --list`
2. Используйте частичное совпадение названия (например, "Logi" вместо полного названия)
3. Убедитесь, что устройство подключено и работает

### Проблема: ID устройств изменяются
**Решение:** Используйте динамическое определение (`USE_DYNAMIC_MEDIA_DETECTION = "true"`) вместо статических ID.

### Проблема: Неправильная камера выбирается
**Решение:** 
1. Уточните название устройства в списке
2. Используйте более специфичное название для поиска
3. Проверьте, что устройство не используется другим приложением
