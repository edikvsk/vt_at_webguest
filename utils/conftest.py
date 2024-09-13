import logging
import subprocess
import time

import psutil
import pytest
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.config import CHROME_DRIVER_PATH
from utils.urls import LOGIN_PAGE_URL

BAT_FILE_PATH = r"C:\Users\Demo\Desktop\VT builds\start_vt.bat"
PROCESS_NAME = "VT_Publisher.exe"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_process_running(process_name):
    """Проверяет, запущен ли процесс с заданным именем."""
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'].lower() == process_name.lower():
            return True
    return False


def run_vt_from_bat():
    """Функция для запуска BAT файла, если процесс не запущен."""
    if not is_process_running(PROCESS_NAME):
        try:
            subprocess.Popen(BAT_FILE_PATH, shell=True)
            time.sleep(10)
            logger.info(f"{PROCESS_NAME} был запущен.")
        except Exception as e:
            logger.error(f"Ошибка при запуске BAT файла: {e}")
    else:
        logger.info(f"{PROCESS_NAME} уже запущен. BAT файл не будет запущен.")


@pytest.fixture(scope="function")
def driver():
    run_vt_from_bat()
    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def login_fixture(driver):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)

    try:
        logger.info("Переходим на страницу логина")
        driver.get(LOGIN_PAGE_URL)
        base_page.click(wg_page.LOGIN_BUTTON)
        yield wg_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении логина: {e}")
        raise
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        raise
