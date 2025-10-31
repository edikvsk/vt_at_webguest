import configparser
import logging
from typing import Optional

import pyperclip
import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.config import (CHROME_DRIVER_PATH, CHROME_BROWSER_PATH, PROCESS_PATH, PROCESS_NAME, SOURCE_TO_PUBLISHING,
                          VIDEO_DEVICE_ID, AUDIO_DEVICE_ID, CONFIG_INI, PUBLISHER_XML_PATH)
from utils.config_manager import config
from utils.desktop_app import DesktopApp
from utils.notificaton_handler import NotificationHandler
from utils.process_handler import ProcessManager
from utils.webrtc_stream_handler import StreamHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True, scope="function")
def ensure_vt_killed_before_test():
    """Гарантированно закрывает VT перед каждым тестом, чтобы избежать зависаний на открытой вкладке."""
    pm = ProcessManager(PROCESS_PATH, PROCESS_NAME, PUBLISHER_XML_PATH)
    pm.kill_process()
    # небольшая пауза, чтобы ОС пересобрала дескрипторы окон
    import time as _t
    _t.sleep(1)


@pytest.fixture(scope="function")
def driver():
    """Основная фикстура для создания WebDriver с настройкой браузера и запуском процесса."""
    # Подавляем WebRTC логи
    import os
    os.environ['WEBRTC_LOGGING'] = '0'
    os.environ['WEBRTC_DEBUG'] = '0'
    
    process_manager = ProcessManager(PROCESS_PATH, PROCESS_NAME, PUBLISHER_XML_PATH)
    process_manager.start_process()

    chrome_options = Options()
    
    # Получаем опции Chrome из конфигурационного менеджера
    chrome_options_list = config.get_chrome_options()
    for option in chrome_options_list:
        chrome_options.add_argument(option)
    
    chrome_options.binary_location = CHROME_BROWSER_PATH

    # Добавляем медиа-ограничения через экспериментальные опции
    media_constraints = {
        "video": {"deviceId": {"exact": VIDEO_DEVICE_ID}},
        "audio": {"deviceId": {"exact": AUDIO_DEVICE_ID}}
    }
    
    # Устанавливаем медиа-ограничения через экспериментальные опции
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.notifications": 1
    })
    
    # Добавляем медиа-ограничения через экспериментальные опции
    chrome_options.add_experimental_option("useAutomationExtension", False)
    # Убираем лишние логи Chrome/ChromeDriver в консоль
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])  # скрыть драйвер-логи
    chrome_options.add_argument("--log-level=3")  # минимизировать уровень логов Chrome

    # Глушим лог-файл chromedriver
    service = Service(CHROME_DRIVER_PATH, log_path=os.devnull)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Максимизируем окно для более стабильной работы
    driver.maximize_window()
    
    # Устанавливаем медиа-ограничения через JavaScript после загрузки страницы
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': f'''
            // Переопределяем getUserMedia для автоматического выбора устройств
            const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
            navigator.mediaDevices.getUserMedia = function(constraints) {{
                console.log('Original constraints:', constraints);
                
                // Сначала получаем список доступных устройств
                return navigator.mediaDevices.enumerateDevices().then(devices => {{
                    console.log('Available devices:', devices);
                    
                    // Ищем устройства по имени (частичное совпадение)
                    const cameraName = "{config.media.camera_for_selection}";
                    const micName = "{config.media.mic_for_selection}";
                    
                    let videoDeviceId = null;
                    let audioDeviceId = null;
                    
                    // Ищем видеоустройство
                    const videoDevices = devices.filter(d => d.kind === 'videoinput');
                    for (const device of videoDevices) {{
                        if (device.label.toLowerCase().includes(cameraName.toLowerCase())) {{
                            videoDeviceId = device.deviceId;
                            console.log('Found video device:', device.label, 'ID:', device.deviceId);
                            break;
                        }}
                    }}
                    
                    // Ищем аудиоустройство
                    const audioDevices = devices.filter(d => d.kind === 'audioinput');
                    for (const device of audioDevices) {{
                        if (device.label.toLowerCase().includes(micName.toLowerCase())) {{
                            audioDeviceId = device.deviceId;
                            console.log('Found audio device:', device.label, 'ID:', device.deviceId);
                            break;
                        }}
                    }}
                    
                    // Формируем constraints с найденными устройствами
                    const modifiedConstraints = {{}};
                    
                    if (constraints.video !== false) {{
                        if (videoDeviceId) {{
                            modifiedConstraints.video = {{ deviceId: {{ exact: videoDeviceId }} }};
                        }} else {{
                            modifiedConstraints.video = true; // Используем первое доступное
                        }}
                    }}
                    
                    if (constraints.audio !== false) {{
                        if (audioDeviceId) {{
                            modifiedConstraints.audio = {{ deviceId: {{ exact: audioDeviceId }} }};
                        }} else {{
                            modifiedConstraints.audio = true; // Используем первое доступное
                        }}
                    }}
                    
                    console.log('Modified constraints:', modifiedConstraints);
                    return originalGetUserMedia.call(this, modifiedConstraints);
                }});
            }};
        '''
    })
    
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def desktop_app_setup():
    """Фикстура для настройки десктопного приложения."""
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)
    return desktop_app, desktop_app_page


@pytest.fixture(scope="function")
def web_guest_page_setup(driver):
    """Фикстура для настройки веб-страницы гостя."""
    web_guest_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    notification_handler = NotificationHandler(driver, web_guest_page.NOTIFICATION_ELEMENT, logger)
    stream_handler = StreamHandler(driver)
    return web_guest_page, base_page, notification_handler, stream_handler


def get_web_url(desktop_app_page: DesktopAppPage, logger: logging.Logger, copy_command: str) -> Optional[str]:
    """
    Упрощённый и быстрый способ получить URL из десктопного приложения.

    Всегда выполняет только "Start Publishing" (без логики переключения) и копирует URL
    через контекстное меню. Используется там, где требуется именно путь через UI.
    """
    try:
        desktop_app_page.focus_click_vt_source_item(SOURCE_TO_PUBLISHING)

        # Всегда пытаемся нажать только Start Publishing (приложение запускается с нуля)
        if desktop_app_page.check_element_enabled_by_title_part("Start Publishing"):
            desktop_app_page.click_button_by_name("Start Publishing")

        # Быстрый клик по пункту копирования без лишних проверок
        desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
        desktop_app_page.click_vt_source_item(copy_command)
        url = pyperclip.paste()
        logger.info(f"Получен URL: {url}")
        return url
    except Exception as e:
        logger.error(f"Ошибка при получении URL: {e}")
        return None


def _read_web_guest_url_from_config(config_path: str) -> Optional[str]:
    """Быстро читает web_guest_page_url из utils/config.ini (без UI)."""
    try:
        parser = configparser.ConfigParser()
        parser.read(config_path, encoding="utf-8")
        url = parser.get("DEFAULT", "web_guest_page_url", fallback=None)
        return url
    except Exception:
        return None


def update_config(config_file_path: str, section: str, key: str, value: str) -> bool:
    """
    Обновляет значение в конфигурационном файле.
    
    Args:
        config_file_path: Путь к файлу конфигурации
        section: Секция конфигурации
        key: Ключ
        value: Значение
        
    Returns:
        True если успешно, False в случае ошибки
    """
    try:
        config = configparser.ConfigParser()
        config.read(config_file_path)
        
        # Создаем секцию если её нет
        if section not in config:
            config.add_section(section)
            
        config[section][key] = value
        
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
        logger.info(f"Конфигурация обновлена: {section}.{key} = {value}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении конфигурации: {e}")
        return False


@pytest.fixture(scope="function")
def login_fixture(driver, logger):
    """Фикстура для авторизации на веб-странице гостя.

    Оптимизации:
    - Только запуск публикации (Start Publishing) без логики переключения.
    - Ссылку получаем через быстрый UI-путь копирования (актуальные динамические URL).
    """
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    web_guest_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    notification_handler = NotificationHandler(driver, web_guest_page.NOTIFICATION_ELEMENT, logger)
    stream_handler = StreamHandler(driver)

    try:
        # 1) Стартуем публикацию только одним действием
        desktop_app_page.focus_click_vt_source_item(SOURCE_TO_PUBLISHING)
        if desktop_app_page.check_element_enabled_by_title_part("Start Publishing"):
            desktop_app_page.click_button_by_name("Start Publishing")

        # 2) Получаем актуальный URL через копирование из UI
        web_guest_url = get_web_url(desktop_app_page, logger, "Copy Web Guest URL")
        if not web_guest_url:
            logger.error("Не удалось получить Web Guest URL через UI.")
            raise ValueError("Web Guest URL не был инициализирован.")

        logger.info("Переходим на страницу Web Guest")
        driver.get(web_guest_url)

        notification_handler.check_notification()
        base_page.click(web_guest_page.LOGIN_BUTTON)
        stream_handler.wait_for_webrtc_connection(timeout=10)
        logger.info("Стрим запущен")

        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")
        raise


@pytest.fixture(scope="function")
def modified_fixture(driver, logger):
    """Фикстура для модифицированной настройки с сохранением URL в конфигурацию."""
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)
    web_guest_page = WebGuestPage(driver)

    try:
        web_guest_url = get_web_url(desktop_app_page, logger, "Copy Web Guest URL")
        if not web_guest_url:
            logger.error("Не удалось получить Web Guest URL.")
            raise ValueError("Web Guest URL не был инициализирован.")

        update_config(CONFIG_INI, 'DEFAULT', 'WEB_GUEST_PAGE_URL', web_guest_url)
        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")
        raise


@pytest.fixture(scope="function")
def web_preview_fixture(driver, logger):
    """Фикстура для настройки веб-превью."""
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)
    web_guest_page = WebGuestPage(driver)

    try:
        web_preview_url = get_web_url(desktop_app_page, logger, "Copy Preview URL")
        if not web_preview_url:
            logger.error("Не удалось получить Preview URL.")
            raise ValueError("Preview URL не был инициализирован.")

        update_config(CONFIG_INI, 'DEFAULT', 'WEB_PREVIEW_PAGE_URL', web_preview_url)
        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")
        raise


@pytest.fixture(scope="function")
def open_web_preview_fixture(driver, logger):
    """Фикстура для открытия веб-превью (ускорённая).

    - Только один клик "Start Publishing" (если доступен).
    - Копируем Preview URL через UI и открываем напрямую в `driver` (не через меню "Open Preview URL").
    """
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)
    web_guest_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    notification_handler = NotificationHandler(driver, web_guest_page.NOTIFICATION_ELEMENT, logger)

    try:
        desktop_app_page.focus_click_vt_source_item(SOURCE_TO_PUBLISHING)
        if desktop_app_page.check_element_enabled_by_title_part("Start Publishing"):
            desktop_app_page.click_button_by_name("Start Publishing")

        preview_url = get_web_url(desktop_app_page, logger, "Copy Preview URL")
        if not preview_url:
            logger.error("Не удалось получить Preview URL через UI.")
            raise ValueError("Preview URL не был инициализирован.")

        logger.info("Переходим на страницу Web Preview")
        driver.get(preview_url)
        notification_handler.check_notification()
        base_page.click(web_guest_page.LOGIN_BUTTON)

        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")
        raise


@pytest.fixture(scope="function")
def test_logger():
    """Фикстура для создания логгера для конкретного теста."""
    import os
    import inspect
    
    # Получаем имя тестового файла
    frame = inspect.currentframe()
    test_file = None
    while frame:
        if 'test_' in frame.f_code.co_filename:
            test_file = frame.f_code.co_filename
            break
        frame = frame.f_back
    
    if test_file:
        test_name = os.path.splitext(os.path.basename(test_file))[0]
    else:
        test_name = "unknown_test"
    
    from utils.logger_config import setup_logger
    return setup_logger(test_name)