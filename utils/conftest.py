import logging

import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.config import CHROME_DRIVER_PATH
from utils.notificaton_handler import NotificationHandler
from utils.process_utils import ProcessManager
from utils.stream_handler import StreamHandler
from utils.urls import WEB_GUEST_PAGE_URL, PROCESS_PATH, PROCESS_NAME

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
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def login_fixture(driver, logger):
    web_guest_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, web_guest_page.NOTIFICATION_ELEMENT, logger)
    stream_handler = StreamHandler(driver)

    try:
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
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        raise
