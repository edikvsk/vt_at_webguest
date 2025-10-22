# Отладка и логирование

Руководство по решению проблем и анализу логов в VT WebGuest Autotests.

## Система логирования

### Структура логов

```
logs/
├── test_start_stream_2025-10-22.log    # Логи конкретного теста
├── VT_Publisher.exe_2025-10-22.log     # Логи процесса VT Publisher
├── ConfigManager_2025-10-22.log        # Логи конфигурации
└── DeviceManager_2025-10-22.log        # Логи медиа-устройств
```

### Уровни логирования

| Уровень | Описание | Когда использовать |
|---------|----------|-------------------|
| `DEBUG` | Детальная отладочная информация | Разработка и отладка |
| `INFO` | Общая информация о работе | Мониторинг выполнения |
| `WARNING` | Предупреждения о потенциальных проблемах | Потенциальные проблемы |
| `ERROR` | Ошибки, не останавливающие выполнение | Обработка ошибок |
| `CRITICAL` | Критические ошибки | Системные сбои |

### Формат логов

```
2025-10-22 13:20:14,659 - DeviceManager - INFO - Найдено устройство: Logi USB Camera (C270 HD WebCam) (ID: c7785e31c99ffb071760...)
```

**Структура**:
- `2025-10-22 13:20:14,659` - Время и дата
- `DeviceManager` - Имя модуля/класса
- `INFO` - Уровень логирования
- `Найдено устройство...` - Сообщение

## Включение отладки

### Переменные окружения

```powershell
# Показать сводку конфигурации
$env:SHOW_CONFIG_SUMMARY = "true"

# Включить подробные логи
$env:LOG_LEVEL = "DEBUG"

# Показать все print() в тестах
$env:PYTEST_S = "true"
```

### Команды для отладки

```powershell
# Проверить конфигурацию
py -3 -c "from utils.config_manager import config; config.print_config_summary()"

# Проверить медиа-устройства
python scripts\test_devices.py

# Запустить тест с подробным выводом
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -TestPath test\smoke\stream_controls\test_start_stream.py -v -s
```

## Типичные проблемы и решения

### 1. Проблемы с медиа-устройствами

#### Устройство не найдено

**Симптомы**:
```
[WARNING] DeviceManager: Устройство с именем 'Logi' не найдено
[WARNING] ConfigManager: Видеоустройство с именем 'Logi' не найдено
```

**Диагностика**:
```powershell
# Просмотреть все доступные устройства
python scripts\test_devices.py

# Проверить подключение устройства
Get-WmiObject -Class Win32_PnPEntity | Where-Object { $_.Name -like "*Logi*" }
```

**Решения**:
1. **Проверить подключение устройства**
2. **Попробовать более общее имя**: `"Camera"`, `"USB"`, `"HD"`
3. **Использовать ручную настройку**:
   ```powershell
   $env:VIDEO_DEVICE_ID = "конкретный_id"
   $env:AUDIO_DEVICE_ID = "конкретный_id"
   ```

#### Ошибка "Overconstrained error"

**Симптомы**:
```
[WARNING] Найдено уведомление: Overconstrained error cannot be applied to unknown camera
```

**Причина**: Chrome не может найти устройство с указанным ID

**Решение**: Система автоматически переключается на fake устройства для стабильной работы

### 2. Проблемы с браузером

#### Chrome не запускается

**Симптомы**:
```
[ERROR] ConfigManager: Chrome Browser: путь не существует
```

**Диагностика**:
```powershell
# Проверить конфигурацию
py -3 -c "from utils.config_manager import config; config.print_config_summary()"

# Проверить наличие Chrome
ls .tools\chrome-Beta\chrome-win64\chrome.exe
```

**Решения**:
1. **Переустановить Chrome**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\install_chrome_beta.ps1
   ```
2. **Указать путь вручную**:
   ```powershell
   $env:CHROME_BROWSER_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
   ```

#### WebDriver не создается

**Симптомы**:
```
selenium.common.exceptions.WebDriverException: Message: unknown error: Chrome failed to start
```

**Решения**:
1. **Проверить версии Chrome и ChromeDriver**
2. **Очистить профиль Chrome**:
   ```powershell
   Remove-Item -Recurse -Force "$env:LOCALAPPDATA\Google\Chrome\User Data\Default"
   ```
3. **Запустить Chrome в безопасном режиме**:
   ```powershell
   $env:BROWSER_HEADLESS = "true"
   ```

### 3. Проблемы с VT Publisher

#### VT Publisher не запускается

**Симптомы**:
```
[ERROR] ProcessManager: VT_Publisher.exe не был запущен
```

**Диагностика**:
```powershell
# Проверить процесс
Get-Process VT_Publisher -ErrorAction SilentlyContinue

# Проверить путь
py -3 -c "from utils.config_manager import config; print(config.desktop.process_path)"
```

**Решения**:
1. **Завершить зависшие процессы**:
   ```powershell
   Get-Process VT_Publisher | Stop-Process -Force
   ```
2. **Проверить права доступа** к папке VT
3. **Переустановить VT Publisher** через автозагрузку

#### Ошибка получения URL

**Симптомы**:
```
[ERROR] Не удалось получить Web Guest URL
```

**Решения**:
1. **Проверить состояние VT Publisher**
2. **Убедиться, что источник выбран** в VT Publisher
3. **Проверить сетевые настройки**

### 4. Проблемы с WebRTC

#### WebRTC стрим не запускается

**Симптомы**:
```
[ERROR] Exception: WebRTC стрим не запущен
```

**Диагностика**:
1. **Открыть Chrome DevTools** (F12)
2. **Перейти в Console**
3. **Проверить ошибки JavaScript**

**Решения**:
1. **Проверить медиа-устройства**:
   ```javascript
   navigator.mediaDevices.enumerateDevices().then(devices => console.log(devices));
   ```
2. **Проверить разрешения**:
   ```javascript
   navigator.permissions.query({name: 'camera'}).then(result => console.log(result));
   ```
3. **Использовать fake устройства** для тестирования

#### Кнопка Connect не кликабельна

**Симптомы**:
```
[ERROR] Элемент не стал кликабельным за 10с: ('xpath', "//button[@type='submit' and @data-cy='connect-button']")
```

**Решения**:
1. **Увеличить таймаут**:
   ```python
   driver.implicitly_wait(30)
   ```
2. **Проверить загрузку страницы**
3. **Очистить кэш браузера**

## Анализ логов

### Поиск ошибок

```powershell
# Найти все ошибки в логах
Select-String -Path "logs\*.log" -Pattern "ERROR|CRITICAL"

# Найти ошибки конкретного теста
Select-String -Path "logs\test_start_stream_*.log" -Pattern "ERROR"
```

### Анализ производительности

```powershell
# Найти медленные операции
Select-String -Path "logs\*.log" -Pattern "Завершен.*[5-9][0-9]\.[0-9]+с"

# Статистика времени выполнения
Select-String -Path "logs\*.log" -Pattern "Завершен.*\([0-9]+\.[0-9]+с\)" | ForEach-Object {
    if ($_.Line -match "\(([0-9]+\.[0-9]+)с\)") {
        [double]$matches[1]
    }
} | Measure-Object -Average -Maximum -Minimum
```

### Мониторинг устройств

```powershell
# Найти все сообщения о устройствах
Select-String -Path "logs\*.log" -Pattern "Найдено устройство|Устройство.*не найдено"

# Статистика найденных устройств
Select-String -Path "logs\*.log" -Pattern "Найдено.*устройств" | ForEach-Object {
    if ($_.Line -match "Найдено (\d+)") {
        [int]$matches[1]
    }
}
```

## Инструменты отладки

### Chrome DevTools

**Использование**:
1. **Открыть DevTools** (F12) во время выполнения теста
2. **Console** - просмотр ошибок JavaScript
3. **Network** - анализ сетевых запросов
4. **Application** - проверка разрешений и устройств

**Полезные команды**:
```javascript
// Список медиа-устройств
navigator.mediaDevices.enumerateDevices().then(devices => console.table(devices));

// Проверка разрешений
navigator.permissions.query({name: 'camera'}).then(result => console.log(result));
navigator.permissions.query({name: 'microphone'}).then(result => console.log(result));

// Состояние WebRTC
navigator.mediaDevices.getUserMedia({video: true, audio: true})
  .then(stream => console.log('Stream active:', stream.active))
  .catch(err => console.error('Error:', err));
```

### PowerShell отладка

```powershell
# Подробный вывод команд
$VerbosePreference = "Continue"
$DebugPreference = "Continue"

# Трассировка выполнения
Set-PSDebug -Trace 1

# Проверка переменных окружения
Get-ChildItem Env: | Where-Object Name -like "*CAMERA*" -or Name -like "*MIC*"
```

### Python отладка

```python
# Включение отладочных логов
import logging
logging.basicConfig(level=logging.DEBUG)

# Точки останова
import pdb; pdb.set_trace()

# Профилирование
import cProfile
cProfile.run('your_function()')
```

## Создание отчетов об ошибках

### Шаблон отчета

```
## Описание проблемы
Краткое описание того, что произошло

## Шаги воспроизведения
1. Команда запуска
2. Ожидаемый результат
3. Фактический результат

## Логи
```
[Вставить релевантные логи]
```

## Конфигурация
- ОС: Windows 10/11
- Python: 3.x
- Chrome: версия
- VT Publisher: версия
- Медиа-устройства: список

## Дополнительная информация
Любая другая полезная информация
```

### Сбор диагностической информации

```powershell
# Создать диагностический отчет
$report = @"
=== VT WebGuest Autotests Diagnostic Report ===
Date: $(Get-Date)

=== System Info ===
OS: $([System.Environment]::OSVersion.VersionString)
PowerShell: $($PSVersionTable.PSVersion)

=== Environment Variables ===
$(Get-ChildItem Env: | Where-Object Name -like "*CAMERA*" -or Name -like "*MIC*" | Format-Table -AutoSize | Out-String)

=== Configuration ===
$(py -3 -c "from utils.config_manager import config; config.print_config_summary()")

=== Media Devices ===
$(python scripts\test_devices.py)

=== Recent Logs ===
$(Get-Content "logs\*.log" | Select-Object -Last 50)
"@

$report | Out-File "diagnostic_report_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').txt"
```

## Лучшие практики отладки

1. **Включайте подробные логи** при разработке
2. **Сохраняйте логи** для анализа проблем
3. **Используйте систематический подход** к диагностике
4. **Документируйте решения** для будущих проблем
5. **Тестируйте исправления** на простых случаях
6. **Мониторьте производительность** регулярно
7. **Создавайте воспроизводимые тесты** для проблем
8. **Используйте версионный контроль** для отслеживания изменений
