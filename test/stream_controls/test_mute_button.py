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
def test_mute_volume(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки MUTE")
    def check_mute_button():
        assert base_page.is_element_present(wg_page.MUTE_BUTTON), "Кнопка MUTE не отображается"

    @log_step(logger, "ШАГ 2. Проверка значка кнопки MUTE - состояние: ВКЛ.")
    def check_mute_image_state_on():
        assert not wg_page.is_button_pressed(wg_page.MUTE_BUTTON), "Кнопка MUTE в состонии ВЫКЛ."

    @log_step(logger, "ШАГ 4. Нажатие кнопки MUTE")
    def turn_off_mute():
        base_page.click(wg_page.MUTE_BUTTON)

    @log_step(logger, "ШАГ 5. Проверка значка кнопки MUTE - состояние: UNMUTE.")
    def check_mute_image_state_off():
        assert wg_page.is_button_pressed(wg_page.MUTE_BUTTON), "Кнопка MUTE в состонии ВКЛ."

    @log_step(logger, "ШАГ 6. Включение MUTE")
    def turn_on_mute():
        base_page.click(wg_page.MUTE_BUTTON)

    try:
        check_mute_button()
        check_mute_image_state_on()
        turn_off_mute()
        check_mute_image_state_off()
        turn_on_mute()
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
