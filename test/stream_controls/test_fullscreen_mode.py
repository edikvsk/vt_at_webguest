import os

import pytest
from selenium.common import NoSuchElementException, TimeoutException

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
def test_fullscreen_mode(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки FullScreen")
    def check_fullscreen_button():
        assert base_page.is_element_present(wg_page.FULLSCREEN_BUTTON), "Кнопка FullScreen не отображается"

    @log_step(logger, "ШАГ 2. Проверка значка кнопки FullScreen - состояние: ВЫКЛ.")
    def check_fullscreen_image_state_off():
        assert wg_page.is_fullscreen_button_pressed(wg_page.FULLSCREEN_BUTTON), "Кнопка FullScreen в состоянии ВКЛ."

    @log_step(logger, "ШАГ 3. Нажатие кнопки/активация FullScreen")
    def turn_on_fullscreen():
        wg_page.hover_element(wg_page.FULLSCREEN_BUTTON)
        base_page.click(wg_page.FULLSCREEN_BUTTON)

    @log_step(logger, "ШАГ 4. Проверка активности состояния FullScreen - состояние: ВКЛ.")
    def check_fullscreen_mode_state_on():
        assert wg_page.is_fullscreen(), "Окно браузера НЕ в состоянии FullScreen"

    @log_step(logger, "ШАГ 5. Проверка значка кнопки FullScreen - состояние: ВКЛ.")
    def check_fullscreen_image_state_on():
        wg_page.hover_element(wg_page.FULLSCREEN_BUTTON)
        assert not wg_page.is_fullscreen_button_pressed(
            wg_page.FULLSCREEN_BUTTON), "Кнопка FullScreen в состоянии ВЫКЛ."

    @log_step(logger, "ШАГ 6. Нажатие кнопки/отключение FullScreen")
    def turn_off_fullscreen():
        wg_page.hover_element(wg_page.FULLSCREEN_BUTTON)
        base_page.click(wg_page.FULLSCREEN_BUTTON)

    @log_step(logger, "ШАГ 7. Проверка активности состояния FullScreen - состояние: ВЫКЛ.")
    def check_fullscreen_mode_state_off():
        assert not wg_page.is_fullscreen(), "Окно браузера в состоянии FullScreen"

    steps = [
        check_fullscreen_button,
        check_fullscreen_image_state_off,
        turn_on_fullscreen,
        check_fullscreen_mode_state_on,
        check_fullscreen_image_state_on,
        turn_off_fullscreen,
        check_fullscreen_mode_state_off

    ]

    for step in steps:
        try:
            step()
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Ошибка при выполнении теста: {e}")
            pytest.fail(f"Ошибка при выполнении теста: {e}")
