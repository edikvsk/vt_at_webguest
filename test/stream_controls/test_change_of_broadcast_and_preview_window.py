import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, login_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_change_of_broadcast_and_preview_window(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки Change Preview")
    def check_change_preview_button():
        wg_page.hover_element(wg_page.PREVIEW_CHANGE_BUTTON)
        assert base_page.is_element_visible(wg_page.PREVIEW_CHANGE_BUTTON), "Кнопка Change Preview не отображается"

    @log_step(logger, "ШАГ 2. Проверка отображения окна Preview - состояние: LOCAL")
    def check_preview_window_state_local():
        result = wg_page.is_element_visible(wg_page.PREVIEW_VOLUME_FADER)
        assert not result, "Окно превью не в состоянии LOCAL"

    @log_step(logger, "ШАГ 3. Нажатие кнопки Change Preview")
    def click_change_preview_button():
        wg_page.hover_element(wg_page.PREVIEW_CHANGE_BUTTON)
        wg_page.click_element_with_scroll(wg_page.PREVIEW_WINDOW)

    @log_step(logger, "ШАГ 4. Проверка отображения окна Preview - состояние: REMOTE")
    def check_preview_window_state_remote():
        result = wg_page.is_element_visible(wg_page.PREVIEW_VOLUME_FADER)
        assert result, "Окно превью не в состоянии REMOTE"

    steps = [
        check_change_preview_button,
        check_preview_window_state_local,
        click_change_preview_button,
        check_preview_window_state_remote
    ]

    for step in steps:
        try:
            step()
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Ошибка при выполнении теста: {e}")
            pytest.fail(f"Ошибка при выполнении теста: {e}")
