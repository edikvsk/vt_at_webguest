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

    volume_fader_value_state_on = '100'
    volume_fader_value_state_off = '0'

    @log_step(logger, "Проверка отображения кнопки MUTE")
    def check_mute_button():
        assert base_page.is_element_present(wg_page.MUTE_BUTTON), "Кнопка MUTE не отображается"

    @log_step(logger, "Проверка значка кнопки MUTE - состояние: ВКЛ.")
    def check_mute_image_state_on():
        assert not wg_page.is_button_pressed(wg_page.MUTE_BUTTON), "Кнопка MUTE в состоянии ВЫКЛ."

    @log_step(logger, "Нажатие кнопки MUTE")
    def turn_off_mute():
        base_page.click(wg_page.MUTE_BUTTON)

    @log_step(logger, "Проверка отображения Volume Fader - состояние: ВКЛ.")
    def check_volume_fader_value_state_on():
        actual_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER)
        assert actual_value == volume_fader_value_state_on, (f"Ожидалось значение '{volume_fader_value_state_on}', но "
                                                             f"получено '{actual_value}'")

    @log_step(logger, "Проверка значка кнопки MUTE - состояние: UNMUTE.")
    def check_mute_image_state_off():
        assert wg_page.is_button_pressed(wg_page.MUTE_BUTTON), "Кнопка MUTE в состоянии ВКЛ."

    @log_step(logger, "Включение MUTE")
    def turn_on_mute():
        base_page.click(wg_page.MUTE_BUTTON)

    @log_step(logger, "Проверка отображения Volume Fader - состояние: ВЫКЛ.")
    def check_volume_fader_value_state_off():
        expected_value = volume_fader_value_state_off
        actual_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER)
        assert actual_value == expected_value, (f"Ожидалось значение '{expected_value}', "
                                                f"но получено '{actual_value}'")

    steps = [
        check_mute_button,
        check_mute_image_state_on,
        turn_off_mute,
        check_volume_fader_value_state_on,
        check_mute_image_state_off,
        turn_on_mute,
        check_volume_fader_value_state_off,
    ]

    for step in steps:
        try:
            step()
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Ошибка при выполнении теста: {e}")
            pytest.fail(f"Ошибка при выполнении теста: {e}")
