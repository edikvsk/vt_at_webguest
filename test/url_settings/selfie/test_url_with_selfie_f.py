import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, modified_url_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.urls import WEB_GUEST_PAGE_URL


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.parametrize("modified_url_fixture",
                         [f"{WEB_GUEST_PAGE_URL}?selfie=f"],
                         indirect=True)
def test_url_selfie_f(modified_url_fixture, driver, logger):
    @log_step(logger, "ШАГ 1. Проверка URL")
    def check_url(drv):
        expected_url = f"{WEB_GUEST_PAGE_URL}?selfie=f"

        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)

    @log_step(logger, "ШАГ 2. Проверка отображения окна Selfie - состояние: ВЫКЛ")
    def check_preview_window_state_off():
        assert not base_page.is_element_present(wg_page.PREVIEW_WINDOW), "Окно Selfie отображается"

    try:
        check_url(driver)
        check_preview_window_state_off()
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
