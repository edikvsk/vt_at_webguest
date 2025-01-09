import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, login_fixture
from utils.desktop_app import DesktopApp
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.urls import PROCESS_PATH
from utils.webrtc_stream_handler import StreamHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_volume_fader_output_audio(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    stream_handler = StreamHandler(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    volume_fader_value_state_off = '0'

    vt_source_name = "mp://mplaylist"

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки MUTE")
    def check_mute_button():
        assert base_page.is_element_present(wg_page.MUTE_BUTTON), "Кнопка MUTE не отображается"

    @log_step(logger, "ШАГ 2. Проверка значка кнопки MUTE - состояние: ВКЛ.")
    def check_mute_image_state_on():
        assert not wg_page.is_button_pressed(wg_page.MUTE_BUTTON), "Кнопка MUTE в состоянии ВЫКЛ."

    @log_step(logger, "ШАГ 3. Включение Output Audio в VT Source Settings")
    def toggle_on_output_audio_vt():
        desktop_app_page.right_click_vt_source_item(vt_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_SOURCE_SETTINGS)
        desktop_app_page.toggle_vt_wg_button(5)
        desktop_app_page.click_button_by_name(desktop_app_page.VT_OK_BUTTON)

    @log_step(logger, "ШАГ 4. Проверка toggle button VT Settings  - состояние: ВЫКЛ.")
    def check_output_audio_toggle_button_state_off():
        expected_value = 0  # Состояние кнопки (0 == False)
        desktop_app_page.right_click_vt_source_item(vt_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_SOURCE_SETTINGS)
        actual_value = desktop_app_page.get_vt_wg_button_state(5)
        desktop_app_page.click_button_by_name(desktop_app_page.VT_OK_BUTTON)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 5. Проверка отображения Volume Fader - состояние: ВЫКЛ.")
    def check_volume_fader_value_state_off():
        expected_value = volume_fader_value_state_off
        actual_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER)
        assert actual_value == expected_value, (f"Ожидалось значение '{expected_value}', "
                                                f"но получено '{actual_value}'")

    @log_step(logger, "Перезапуск стрима для обновления WebRTC stats")
    def restart_streaming():
        wg_page.hover_element(wg_page.PREVIEW_WINDOW)
        base_page.click(wg_page.STOP_BUTTON)
        base_page.click(wg_page.START_BUTTON)
        assert wg_page.is_button_pressed(wg_page.STOP_BUTTON), "Кнопка STOP не отображается"

    @log_step(logger, "ШАГ 6. Проверка аудиопотока - состояние: ВЫКЛ.")
    def check_audio_stream_state_off():
        assert not stream_handler.is_audio_stream_active(), "Присутствует аудиопоток"

    @log_step(logger, "ШАГ 7. Установка значения Volume Fader")
    def set_volume_fader_value():
        # список значений для тестирования
        value = 50

        wg_page.hover_element(wg_page.VOLUME_FADER)
        wg_page.set_volume_fader_value(wg_page.VOLUME_FADER, value)

        # Получаем текущее значение слайдера
        current_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER)

        # Проверяем, что текущее значение соответствует установленному
        assert current_value == str(value), f"Ошибка: ожидаемое значение {value}, получено {current_value}"

    @log_step(logger, "ШАГ 8. Отключение Output Audio в VT Source Settings")
    def toggle_off_output_audio_vt():
        desktop_app_page.right_click_vt_source_item(vt_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_SOURCE_SETTINGS)
        desktop_app_page.toggle_vt_wg_button(5)
        desktop_app_page.click_button_by_name(desktop_app_page.VT_OK_BUTTON)

    @log_step(logger, "ШАГ 9. Проверка toggle button VT Settings  - состояние: ВКЛ.")
    def check_output_audio_toggle_button_state_on():
        expected_value = 1  # Состояние кнопки (1 == True)
        desktop_app_page.right_click_vt_source_item(vt_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_SOURCE_SETTINGS)
        actual_value = desktop_app_page.get_vt_wg_button_state(5)
        desktop_app_page.click_button_by_name(desktop_app_page.VT_OK_BUTTON)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 10. Проверка аудиопотока - состояние: ВКЛ.")
    def check_audio_stream_state_on():
        assert stream_handler.is_audio_stream_active(), "Аудиопоток отстутствует"

    @log_step(logger, "ШАГ 11. Установка значений Volume Fader")
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
        check_mute_button,
        check_mute_image_state_on,
        toggle_on_output_audio_vt,
        check_output_audio_toggle_button_state_off,
        check_volume_fader_value_state_off,
        restart_streaming,
        check_audio_stream_state_off,
        set_volume_fader_value,
        restart_streaming,
        check_audio_stream_state_off,
        toggle_off_output_audio_vt,
        check_output_audio_toggle_button_state_on,
        restart_streaming,
        check_audio_stream_state_on,
        set_multiple_volume_fader_values
    ]

    for step in steps:
        try:
            step()
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Ошибка при выполнении теста: {e}")
            pytest.fail(f"Ошибка при выполнении теста: {e}")
