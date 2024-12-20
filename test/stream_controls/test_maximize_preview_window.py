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
def test_maximize_preview_window(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки Minimize Preview")
    def check_minimize_preview_button():
        wg_page.hover_element(wg_page.PREVIEW_MINIMIZE_BUTTON)
        assert base_page.is_element_visible(wg_page.PREVIEW_MINIMIZE_BUTTON), "Кнопка Minimize Preview не отображается"

    @log_step(logger, "ШАГ 2. Проверка отображения окна Preview - состояние: ВКЛ")
    def check_preview_window_state_on():
        assert base_page.is_element_present(wg_page.PREVIEW_WINDOW), "Окно превью НЕ отображается"

    @log_step(logger, "ШАГ 3. Нажатие кнопки Maximize Preview")
    def click_maximize_preview_button():
        wg_page.hover_element(wg_page.PREVIEW_MINIMIZE_BUTTON)
        base_page.click(wg_page.PREVIEW_MINIMIZE_BUTTON)

    @log_step(logger, "ШАГ 4. Проверка отображения окна Preview - состояние: ВЫКЛ")
    def check_preview_window_state_off():
        assert base_page.is_element_present(wg_page.PREVIEW_WINDOW), "Окно превью отображается"

    @log_step(logger, "ШАГ 5. Проверка отображения кнопки Maximize Preview")
    def check_maximize_preview_button():
        wg_page.hover_element(wg_page.PREVIEW_MINIMIZE_BUTTON)
        assert wg_page.is_element_visible(wg_page.PREVIEW_MINIMIZE_BUTTON), "Кнопка Maximize Preview НЕ отображается"

    @log_step(logger, "ШАГ 6. Нажатие кнопки Maximize Preview")
    def click_maximize_preview_button_after_maximize():
        wg_page.hover_element(wg_page.PREVIEW_MINIMIZE_BUTTON)
        base_page.click(wg_page.PREVIEW_MINIMIZE_BUTTON)

    @log_step(logger, "ШАГ 7. Проверка отображения окна Preview - состояние: ВКЛ")
    def check_preview_window_state_on_after_maximize():
        assert base_page.is_element_present(wg_page.PREVIEW_WINDOW), "Окно превью НЕ отображается"

    @log_step(logger, "ШАГ 8. Проверка отображения кнопки Minimize Preview")
    def check_minimize_preview_button_after_maximize():
        wg_page.hover_element(wg_page.PREVIEW_MINIMIZE_BUTTON)
        assert wg_page.is_element_visible(wg_page.PREVIEW_MINIMIZE_BUTTON), "Кнопка Minimize Preview НЕ отображается"

    steps = [
        check_maximize_preview_button,
        check_preview_window_state_on,
        click_maximize_preview_button,
        check_preview_window_state_off,
        check_maximize_preview_button,
        click_maximize_preview_button_after_maximize,
        check_preview_window_state_on_after_maximize,
        check_minimize_preview_button_after_maximize
    ]

    for step in steps:
        try:
            step()
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Ошибка при выполнении теста: {e}")
            pytest.fail(f"Ошибка при выполнении теста: {e}")
