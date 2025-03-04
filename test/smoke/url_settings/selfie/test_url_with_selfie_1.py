import configparser
import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.config import CONFIG_INI
from utils.conftest import driver, modified_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("modified_fixture")
def test_url_with_selfie_1(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)
    web_guest_url = config['DEFAULT']['WEB_GUEST_PAGE_URL'].strip()

    @log_step(logger, "Проверка URL")
    def check_url(drv):
        drv.get(web_guest_url + "?selfie=1")
        expected_url = f"{web_guest_url}?selfie=1"

        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)

    @log_step(logger, "Проверка отображения окна Selfie - состояние: ВКЛ")
    def check_preview_window_state_on():
        assert base_page.is_element_present(wg_page.PREVIEW_WINDOW), "Окно Selfie НЕ отображается"

    try:
        check_url(driver)
        check_preview_window_state_on()
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
