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
def test_volume_fader_preview_window(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)

    volume_fader_value_state_on = '100'
    volume_fader_value_state_off = '0'

    @log_step(logger, "Проверка отображения кнопки Change Preview")
    def check_change_preview_button():
        wg_page.hover_element(wg_page.PREVIEW_CHANGE_BUTTON)
        assert base_page.is_element_visible(wg_page.PREVIEW_CHANGE_BUTTON), "Кнопка Change Preview не отображается"

    @log_step(logger, "Проверка отображения окна Preview - состояние: LOCAL")
    def check_preview_window_state_local():
        result = wg_page.is_element_visible(wg_page.PREVIEW_VOLUME_FADER)
        assert not result, "Окно превью не в состоянии LOCAL"

    @log_step(logger, "Нажатие кнопки Change Preview")
    def click_change_preview_button():
        wg_page.hover_element(wg_page.PREVIEW_CHANGE_BUTTON)
        wg_page.click_element_with_scroll(wg_page.PREVIEW_WINDOW)

    @log_step(logger, "Проверка отображения окна Preview - состояние: REMOTE")
    def check_preview_window_state_remote():
        result = wg_page.is_element_visible(wg_page.PREVIEW_VOLUME_FADER)
        assert result, "Окно превью не в состоянии REMOTE"

    @log_step(logger, "Проверка значка кнопки MUTE - состояние: ВКЛ.")
    def check_mute_image_state_on():
        assert not wg_page.is_button_pressed(wg_page.PREVIEW_MUTE_BUTTON), "Кнопка MUTE в состоянии ВЫКЛ."

    @log_step(logger, "Проверка отображения Volume Fader - состояние: ВЫКЛ.")
    def check_volume_fader_value_state_off():
        expected_value = volume_fader_value_state_off
        actual_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER_PREVIEW)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Установка значения Volume Fader")
    def set_volume_fader_value():
        value = 100
        wg_page.hover_element(wg_page.VOLUME_FADER_PREVIEW)
        wg_page.set_volume_fader_value(wg_page.VOLUME_FADER_PREVIEW, value)
        current_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER_PREVIEW)
        assert current_value == str(value), f"Ошибка: ожидаемое значение {value}, получено {current_value}"

    @log_step(logger, "Проверка отображения Volume Fader - состояние: ВКЛ.")
    def check_volume_fader_value_state_on():
        expected_value = volume_fader_value_state_on
        actual_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER_PREVIEW)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Проверка значка кнопки MUTE - состояние: UNMUTE.")
    def check_mute_image_state_off():
        assert wg_page.is_button_pressed(wg_page.PREVIEW_MUTE_BUTTON), "Кнопка MUTE в состоянии ВКЛ."

    steps = [
        check_change_preview_button,
        check_preview_window_state_local,
        click_change_preview_button,
        check_preview_window_state_remote,
        check_mute_image_state_on,
        check_volume_fader_value_state_off,
        set_volume_fader_value,
        check_volume_fader_value_state_on,
        check_mute_image_state_off
    ]

    for step in steps:
        try:
            step()
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Ошибка при выполнении теста: {e}")
            pytest.fail(f"Ошибка при выполнении теста: {e}")
