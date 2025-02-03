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
    process_manager = ProcessManager(PROCESS_PATH, PROCESS_NAME)
    process_manager.start_process()

    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--enable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.binary_location = CHROME_BROWSER_PATH

    media_constraints = {
        "video": {"deviceId": {"exact": VIDEO_DEVICE_ID}},
        "audio": {"deviceId": {"exact": AUDIO_DEVICE_ID}}
    }
    chrome_options.add_argument(f"mediaStreamConstraints={media_constraints}")

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    yield driver
    driver.quit()


def get_web_url(desktop_app_page, logger, copy_command):
    desktop_app_page.focus_click_vt_source_item(SOURCE_TO_PUBLISHING)
    is_enabled_start_publishing = desktop_app_page.check_element_enabled_by_title_part("Start Publishing")
    is_enabled_stop_publishing = desktop_app_page.check_element_enabled_by_title_part("Stop Publishing")

    if is_enabled_start_publishing and not is_enabled_stop_publishing:
        desktop_app_page.click_button_by_name("Start Publishing")
        desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
        desktop_app_page.click_vt_source_item(copy_command)
        return pyperclip.paste()
    elif not is_enabled_start_publishing and is_enabled_stop_publishing:
        desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
        desktop_app_page.click_vt_source_item(copy_command)
        logger.info("Паблишинг выбранного источника уже осуществляется. Продолжаем тест.")
        return pyperclip.paste()
    else:
        logger.info("Кнопка 'Start Publishing' отключена, клик не выполнен. Продолжаем тест.")
        return None


def update_config(config_file_path, section, key, value):
    config = configparser.ConfigParser()
    config.read(config_file_path)
    config[section][key] = value
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)


@pytest.fixture(scope="function")
def login_fixture(driver, logger):
    web_guest_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, web_guest_page.NOTIFICATION_ELEMENT, logger)
    stream_handler = StreamHandler(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    try:
        WEB_GUEST_PAGE_URL = get_web_url(desktop_app_page, logger, "Copy Web Guest URL")
        if not WEB_GUEST_PAGE_URL:
            logger.error("Не удалось получить Web Guest URL.")
            raise ValueError("Web Guest URL не был инициализирован.")

        logger.info("Переходим на страницу Web Guest")
        driver.get(WEB_GUEST_PAGE_URL)
        base_page = BasePage(driver)

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
    web_guest_page = WebGuestPage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    try:
        WEB_GUEST_PAGE_URL = get_web_url(desktop_app_page, logger, "Copy Web Guest URL")
        if not WEB_GUEST_PAGE_URL:
            logger.error("Не удалось получить Web Guest URL.")
            raise ValueError("Web Guest URL не был инициализирован.")

        update_config(CONFIG_INI, 'DEFAULT', 'WEB_GUEST_PAGE_URL', WEB_GUEST_PAGE_URL)
        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")


@pytest.fixture(scope="function")
def web_preview_fixture(driver, logger):
    web_guest_page = WebGuestPage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    try:
        WEB_PREVIEW_PAGE_URL = get_web_url(desktop_app_page, logger, "Copy Preview URL")
        if not WEB_PREVIEW_PAGE_URL:
            logger.error("Не удалось получить Preview URL.")
            raise ValueError("Preview URL не был инициализирован.")

        update_config(CONFIG_INI, 'DEFAULT', 'WEB_PREVIEW_PAGE_URL', WEB_PREVIEW_PAGE_URL)
        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")


@pytest.fixture(scope="function")
def open_web_preview_fixture(driver, logger):
    base_page = BasePage(driver)
    web_guest_page = WebGuestPage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)
    notification_handler = NotificationHandler(driver, web_guest_page.NOTIFICATION_ELEMENT, logger)

    try:
        desktop_app_page.focus_click_vt_source_item(SOURCE_TO_PUBLISHING)
        is_enabled_start_publishing = desktop_app_page.check_element_enabled_by_title_part("Start Publishing")
        is_enabled_stop_publishing = desktop_app_page.check_element_enabled_by_title_part("Stop Publishing")

        if is_enabled_start_publishing and not is_enabled_stop_publishing:
            desktop_app_page.click_button_by_name("Start Publishing")
            desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
            desktop_app_page.click_vt_source_item("Open Preview URL")
        elif not is_enabled_start_publishing and is_enabled_stop_publishing:
            desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
            desktop_app_page.click_vt_source_item("Open Preview URL")
            logger.info("Паблишинг выбранного источника уже осуществляется. Продолжаем тест.")
        else:
            logger.info("Кнопка 'Start Publishing' отключена, клик не выполнен. Продолжаем тест.")

        logger.info("Переходим на страницу Web Preview")
        notification_handler.check_notification()
        base_page.click(web_guest_page.LOGIN_BUTTON)

        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")
