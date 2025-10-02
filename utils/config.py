"""
Модуль конфигурации для автотестов VT WebGuest.
Теперь использует улучшенный ConfigManager с поддержкой переменных окружения.
"""

# Импортируем новый менеджер конфигурации
from utils.config_manager import config

# Экспортируем константы для обратной совместимости
CHROME_DRIVER_PATH = config.browser.chrome_driver_path
CHROME_BROWSER_PATH = config.browser.chrome_browser_path
CONFIG_INI = config.desktop.config_ini_path
PROCESS_PATH = config.desktop.process_path
PROCESS_NAME = config.desktop.process_name
PUBLISHER_XML_PATH = config.desktop.publisher_xml_path
SOURCE_TO_PUBLISHING = config.desktop.source_to_publishing
VIDEO_DEVICE_ID = config.media.video_device_id
AUDIO_DEVICE_ID = config.media.audio_device_id
CAMERA_FOR_SELECTION_IN_TEST_CAMERA_SELECT = config.media.camera_for_selection
MIC_FOR_SELECTION_IN_TEST_MICROPHONE_SELECT = config.media.mic_for_selection

# Валидируем конфигурацию при импорте
if not config.validate_config():
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Конфигурация содержит ошибки. Некоторые тесты могут работать некорректно.")

# Выводим сводку конфигурации в режиме отладки
import os
if os.getenv('SHOW_CONFIG_SUMMARY', '').lower() in ('true', '1', 'yes'):
    config.print_config_summary()
