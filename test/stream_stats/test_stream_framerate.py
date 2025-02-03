import configparser
import os
import time

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.config import CONFIG_INI
from utils.conftest import driver, modified_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.webrtc_stream_handler import StreamHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("modified_fixture")
def test_stream_framerate(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)
    web_guest_url = config['DEFAULT']['WEB_GUEST_PAGE_URL'].strip()
    driver.get(web_guest_url)

    base_page = BasePage(driver)
    wg_page = WebGuestPage(driver)
    stream_handler = StreamHandler(driver)

    @log_step(logger, "Проверка отображения Authorization Form")
    def check_authorization_form():
        assert base_page.is_element_visible(wg_page.AUTHORIZATION_FORM), "Authorization Form не отображается"

    @log_step(logger, "Логин")
    def login():
        base_page.click(wg_page.LOGIN_BUTTON)
        assert base_page.is_element_visible(wg_page.STOP_BUTTON), "Логин НЕ выполнен"

    @log_step(logger, "Проверка FPS")
    def check_fps():
        time.sleep(5)
        print(stream_handler.is_video_stream_active())
        fps = stream_handler.calculate_average_stream_fps()
        print(fps)

    try:
        check_authorization_form(),
        login(),
        check_fps()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
