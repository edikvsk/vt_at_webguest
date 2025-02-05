import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.config import PROCESS_PATH
from utils.conftest import driver, login_fixture
from utils.desktop_app import DesktopApp
from utils.helpers import log_step
from utils.logger_config import setup_logger


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_audio_channels_volume_fader(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_web_guest_source_name = "Web Guest"
    audio_channels_value = "1, 2"
    volume_fader_value_state_on = '100'

    @log_step(logger, "Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "Нажатие кнопки SETTINGS")
    def click_settings_button():
        base_page.click(wg_page.SETTINGS_BUTTON)
        assert wg_page.is_element_visible(wg_page.WG_SETTINGS_WINDOW), "Settings не открыты"

    @log_step(logger, "Выбор Audio Channels")
    def select_audio_channels():
        wg_page.select_audio_channels(audio_channels_value)
        base_page.click(wg_page.COMBOBOX_BACK_BUTTON)

    @log_step(logger, "Проверка значения AudioChannels в VT WebGuest Settings")
    def check_audio_channels_field_value_vt():
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        value_list = desktop_app_page.get_combobox_item_name_by_index(7, 0)
        actual_value = value_list[0] if value_list else None  # звлекаем строку из списка
        expected_value = audio_channels_value
        desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)
        desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'."

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

    @log_step(logger, "Установка значений Volume Fader")
    def set_multiple_volume_fader_values():
        # список значений для тестирования
        test_values = [0, 25, 50, 75, 100]

        for value in test_values:
            wg_page.hover_element(wg_page.VOLUME_FADER)
            wg_page.set_volume_fader_value_with_events(wg_page.VOLUME_FADER, value)

            # Получаем текущее значение слайдера
            current_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER)

            # Проверяем, что текущее значение соответствует установленному
            assert current_value == str(value), f"Ошибка: ожидаемое значение {value}, получено {current_value}"

    steps = [
        check_settings_button,
        click_settings_button,
        select_audio_channels,
        check_audio_channels_field_value_vt,
        turn_off_mute,
        check_volume_fader_value_state_on,
        check_mute_image_state_off,
        set_multiple_volume_fader_values
    ]

    for step in steps:
        try:
            step()
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Ошибка при выполнении теста: {e}")
            pytest.fail(f"Ошибка при выполнении теста: {e}")

        # При необходимости закрыть VT
        # finally:

        # desktop_app.close_application()
