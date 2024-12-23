import logging

import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
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

    # пути к ChromeDriver и Chrome браузеру
    chrome_driver_path = "D:/chromedriver/chromedriver.exe"
    chrome_browser_path = "C:/Program Files/Google/Chrome Beta/Application/chrome.exe"

    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.binary_location = chrome_browser_path

    media_constraints = {
        "video": {
            "deviceId": {
                "exact": "8381375a5322592502987a99a4a57727661cfbf29116e845f10b766767ae596f"
            }
        },
        "audio": {
            "deviceId": {
                "exact": "e583fb0c4b6e4c2aa41ebbab2784cc771351bc711de849a1d2dd86f21529bd11"
            }
        }
    }

    chrome_options.add_argument(f"mediaStreamConstraints={media_constraints}")
    service = Service(chrome_driver_path)  # указанный путь к ChromeDriver
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


@pytest.fixture(scope="function")
def modified_url_fixture(driver, logger, request):
    url = request.param  # Получаем параметр из запроса
    web_guest_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, web_guest_page.NOTIFICATION_ELEMENT, logger)
    stream_handler = StreamHandler(driver)

    try:
        logger.info("Переходим на страницу Web Guest")
        driver.get(url)  # Используем переданный URL

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
