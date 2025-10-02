1. Проверка конфигурации

```bash
py -3 -c "from utils.config_manager import config; config.print_config_summary()"
```

### 2. Доступные тесты

```bash
py -3 -m pytest --collect-only -q
```

**Результат:** Найдено **91 тест** в различных категориях!

##  Примеры запуска тестов

### Простой запуск одного теста
```bash
py -3 -m pytest test/smoke/stream_controls/test_start_stream.py -v
```

### Запуск по категориям
```bash
# Негативные тесты
py -3 -m pytest test/smoke/negative_cases/ -v

# Тесты настроек WebGuest  
py -3 -m pytest test/smoke/wg_settings/ -v

# Тесты управления стримом
py -3 -m pytest test/smoke/stream_controls/ -v

# Регрессионные тесты
py -3 -m pytest test/regress/ -v
```

### Запуск с маркерами
```bash
# Только smoke тесты
py -3 -m pytest -m smoke -v

# Быстрые тесты
py -3 -m pytest -m fast -v

# Тесты разрешения
py -3 -m pytest -m resolution -v

# Тесты без требований к оборудованию
py -3 -m pytest -m "not requires_camera and not requires_microphone" -v
```

### С улучшенным логированием
```bash
# Подробное логирование
LOG_LEVEL=DEBUG py -3 -m pytest test/smoke/stream_controls/test_start_stream.py -v -s

# Показать сводку конфигурации
SHOW_CONFIG_SUMMARY=true py -3 -m pytest --collect-only -q
```

##  Настройка через переменные окружения

```bash
# Настройки браузера
set BROWSER_HEADLESS=true
set BROWSER_WINDOW_WIDTH=1280
set BROWSER_WINDOW_HEIGHT=720

# Настройки тестов
set TEST_DEFAULT_TIMEOUT=15
set TEST_RETRY_COUNT=5
set TEST_SCREENSHOT_ON_FAILURE=true

# Настройки логирования
set LOG_LEVEL=DEBUG
set LOG_CONSOLE=true
set LOG_FILE=true

# Затем запускаем тест
py -3 -m pytest test/smoke/stream_controls/test_start_stream.py -v
```

## Доступные маркеры

```bash
py -3 -m pytest --markers
```

**Основные маркеры:**
- `@pytest.mark.smoke` - Smoke тесты
- `@pytest.mark.negative` - Негативные тесты  
- `@pytest.mark.fast` - Быстрые тесты
- `@pytest.mark.slow` - Медленные тесты
- `@pytest.mark.requires_camera` - Требует камеру
- `@pytest.mark.stream_controls` - Тесты управления стримом

##  Отладка

1. **Проверить конфигурацию:**
   ```bash
   py -3 -c "from utils.config_manager import config; config.validate_config()"
   ```

2. **Включить подробное логирование:**
   ```bash
   LOG_LEVEL=DEBUG py -3 -m pytest your_test.py -v -s
   ```

3. **Показать сводку конфигурации:**
   ```bash
   SHOW_CONFIG_SUMMARY=true py -3 -c "from utils.config import *"
   ```
