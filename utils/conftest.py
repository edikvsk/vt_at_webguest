import configparser
import logging

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
                          VIDEO_DEVICE_ID, AUDIO_DEVICE_ID, CONFIG_INI)
from utils.desktop_app import DesktopApp
from utils.notificaton_handler import NotificationHandler
from utils.process_handler import ProcessManager
from utils.webrtc_stream_handler import StreamHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def driver():
    # Создаем экземпляр ProcessManager
    process_manager = ProcessManager(PROCESS_PATH, PROCESS_NAME)

    # Запускаем процесс, если он не запущен
    process_manager.start_process()

    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    # chrome_options.add_argument("--use-fake-device-for-media-stream") # Использовать если недоступно физ. устройство
    chrome_options.binary_location = CHROME_BROWSER_PATH  # Используем путь из конфигурации

    media_constraints = {
        "video": {
            "deviceId": {
                "exact": VIDEO_DEVICE_ID
            }
        },
        "audio": {
            "deviceId": {
                "exact": AUDIO_DEVICE_ID
            }
        }
    }

    chrome_options.add_argument(f"mediaStreamConstraints={media_constraints}")
    service = Service(CHROME_DRIVER_PATH)  # Используем путь из конфигурации
    driver = webdriver.Chrome(service=service, options=chrome_options)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def login_fixture(driver, logger):
    web_guest_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, web_guest_page.NOTIFICATION_ELEMENT, logger)
    stream_handler = StreamHandler(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    WEB_GUEST_PAGE_URL = ""

    try:
        desktop_app_page.focus_click_vt_source_item(SOURCE_TO_PUBLISHING)
        is_enabled_start_publishing = desktop_app_page.check_element_enabled_by_title_part("Start Publishing")
        is_enabled_stop_publishing = desktop_app_page.check_element_enabled_by_title_part("Stop Publishing")

        if is_enabled_start_publishing and not is_enabled_stop_publishing:
            desktop_app_page.click_button_by_name("Start Publishing")
            desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
            desktop_app_page.click_vt_source_item("Copy Web Guest URL")
            WEB_GUEST_PAGE_URL = pyperclip.paste()
        elif not is_enabled_start_publishing and is_enabled_stop_publishing:
            desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
            desktop_app_page.click_vt_source_item("Copy Web Guest URL")
            WEB_GUEST_PAGE_URL = pyperclip.paste()
            logger.info("Паблишинг выбранного источника уже осуществляется. Продолжаем тест.")
        else:
            logger.info("Кнопка 'Start Publishing' отключена, клик не выполнен. Продолжаем тест.")

        if not WEB_GUEST_PAGE_URL:
            logger.error("Не удалось получить Web Guest URL.")
            raise ValueError("Web Guest URL не был инициализирован.")

        logger.info("Переходим на страницу Web Guest")
        driver.get(WEB_GUEST_PAGE_URL)

        base_page = BasePage(driver)

        # Проверка уведомлений
        notification_handler.check_notification()

        base_page.click(web_guest_page.LOGIN_BUTTON)

        # Ожидание подключения WebRTC стрима
        stream_handler.wait_for_webrtc_connection(timeout=10)
        logger.info("Стрим запущен")

        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")
        raise
    return WEB_GUEST_PAGE_URL


@pytest.fixture(scope="function")
def modified_fixture(driver, logger):
    web_guest_page = WebGuestPage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    WEB_GUEST_PAGE_URL = ""

    try:
        desktop_app_page.focus_click_vt_source_item(SOURCE_TO_PUBLISHING)
        is_enabled_start_publishing = desktop_app_page.check_element_enabled_by_title_part("Start Publishing")
        is_enabled_stop_publishing = desktop_app_page.check_element_enabled_by_title_part("Stop Publishing")

        if is_enabled_start_publishing and not is_enabled_stop_publishing:
            desktop_app_page.click_button_by_name("Start Publishing")
            desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
            desktop_app_page.click_vt_source_item("Copy Web Guest URL")
            WEB_GUEST_PAGE_URL = pyperclip.paste()
        elif not is_enabled_start_publishing and is_enabled_stop_publishing:
            desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
            desktop_app_page.click_vt_source_item("Copy Web Guest URL")
            WEB_GUEST_PAGE_URL = pyperclip.paste()
            logger.info("Паблишинг выбранного источника уже осуществляется. Продолжаем тест.")
        else:
            logger.info("Кнопка 'Start Publishing' отключена, клик не выполнен. Продолжаем тест.")

        if not WEB_GUEST_PAGE_URL:
            logger.error("Не удалось получить Web Guest URL.")
            raise ValueError("Web Guest URL не был инициализирован.")

        logger.info("Переходим на страницу Web Guest")

        # Обновляем файл конфигурации
        config_file_path = CONFIG_INI
        config = configparser.ConfigParser()
        config.read(config_file_path)

        # Обновляем значение в конфигурации
        config['DEFAULT']['WEB_GUEST_PAGE_URL'] = WEB_GUEST_PAGE_URL

        # Записываем изменения обратно в файл
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")


@pytest.fixture(scope="function")
def web_preview_fixture(driver, logger):
    web_guest_page = WebGuestPage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    WEB_PREVIEW_PAGE_URL = ""

    try:
        desktop_app_page.focus_click_vt_source_item(SOURCE_TO_PUBLISHING)
        is_enabled_start_publishing = desktop_app_page.check_element_enabled_by_title_part("Start Publishing")
        is_enabled_stop_publishing = desktop_app_page.check_element_enabled_by_title_part("Stop Publishing")

        if is_enabled_start_publishing and not is_enabled_stop_publishing:
            desktop_app_page.click_button_by_name("Start Publishing")
            desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
            desktop_app_page.click_vt_source_item("Copy Preview URL")
            WEB_PREVIEW_PAGE_URL = pyperclip.paste()
        elif not is_enabled_start_publishing and is_enabled_stop_publishing:
            desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
            desktop_app_page.click_vt_source_item("Copy Preview URL")
            WEB_PREVIEW_PAGE_URL = pyperclip.paste()
            logger.info("Паблишинг выбранного источника уже осуществляется. Продолжаем тест.")
        else:
            logger.info("Кнопка 'Start Publishing' отключена, клик не выполнен. Продолжаем тест.")

        if not WEB_PREVIEW_PAGE_URL:
            logger.error("Не удалось получить Preview URL.")
            raise ValueError("Preview URL не был инициализирован.")

        logger.info("Переходим на страницу Web Preview")

        # Обновляем файл конфигурации
        config_file_path = CONFIG_INI
        config = configparser.ConfigParser()
        config.read(config_file_path)

        # Обновляем значение в конфигурации
        config['DEFAULT']['WEB_PREVIEW_PAGE_URL'] = WEB_PREVIEW_PAGE_URL

        # Записываем изменения обратно в файл
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")
