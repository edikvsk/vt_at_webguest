import os

import pytest
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait

from pages.login_page import LoginPage
from utils.config import CHROME_DRIVER_PATH, USERNAME, LOCATION
from utils.logger_config import setup_logger
from utils.urls import LOGIN_PAGE_URL


@pytest.fixture(scope="function")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--media-stream-id=62e81b2a3bfe8844470fbfc1739f77582582b4142c0e7e1df6da772dc6648855")
    chrome_options.add_argument(
        "--media-device-id-video=62e81b2a3bfe8844470fbfc1739f77582582b4142c0e7e1df6da772dc6648855")
    chrome_options.add_argument(
        "--media-device-id-audio=62e81b2a3bfe8844470fbfc1739f77582582b4142c0e7e1df6da772dc6648855")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Разрешить доступ к камере и микрофону
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    yield driver
    driver.quit()


@pytest.fixture
def login_fixture(driver):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)

    try:
        driver.get(LOGIN_PAGE_URL)
        login_page = LoginPage(driver)
        login_page.enter_username(USERNAME)
        login_page.enter_location(LOCATION)
        login_page.click_login_button()

        wait = WebDriverWait(driver, 20)
        # wait.until(EC.url_contains(XMEDIA_PAGE_URL))

        yield login_page
    except NoSuchElementException as e:
        logger.error("Element not found: %s", e)
        raise
    except TimeoutException as e:
        logger.error("Timeout exceeded: %s", e)
        raise
    except Exception as e:
        logger.error("An error occurred during the fixture execution: %s", e)
        raise
