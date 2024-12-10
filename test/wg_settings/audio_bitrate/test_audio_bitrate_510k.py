import os
import time

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, login_fixture
from utils.desktop_app import DesktopApp
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.stream_handler import StreamHandler
from utils.urls import PROCESS_PATH


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_audio_bitrate_510k(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    stream_handler = StreamHandler(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_web_guest_source_name = "Web Guest"
    audio_bitrate = "AUDIO BITRATE\n510K"

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "ШАГ 2. Нажатие кнопки SETTINGS")
    def click_settings_button():
        base_page.click(wg_page.SETTINGS_BUTTON)

    @log_step(logger, "ШАГ 3. Выбор Audio Bitrate")
    def select_audio_bitrate():
        time.sleep(3.5)
        wg_page.select_audio_bitrate(audio_bitrate)
        base_page.click(wg_page.COMBOBOX_BACK_BUTTON)
        expected_value = audio_bitrate
        actual_value = wg_page.get_settings_item_value_text(wg_page.AUDIO_BITRATE_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 4. Проверка значения Audio Bitrate в VT WebGuest Settings")
    def check_audio_bitrate_field_value_vt():
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        desktop_app_page.select_combobox_item_by_index(6, 6)
        desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)

    @log_step(logger, "ШАГ 5. Проверка значения поля Audio Bitrate")
    def check_audio_bitrate_field_value():
        expected_value = audio_bitrate
        actual_value = wg_page.get_settings_item_value_text(wg_page.AUDIO_BITRATE_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 6. Запуск мониторинга битрейта")
    def monitor_bitrate():
        result = stream_handler.start_monitoring_bitrate()
        formatted_audio_bitrate = stream_handler.format_audio_bitrate(result['maxAudio'])
        average_audio_bitrate = result['averageAudio']
        max_audio_bitrate = result['maxAudio']

        logger.info(f'Average Audio Bitrate: {average_audio_bitrate} kb/s')
        logger.info(f'Max Audio Bitrate: {max_audio_bitrate} kb/s')

        assert formatted_audio_bitrate == audio_bitrate, (f"Ожидалось значение '{audio_bitrate}',"
                                                          f" но получено '{formatted_audio_bitrate}'")

    steps = [
        check_settings_button,
        click_settings_button,
        select_audio_bitrate,
        check_audio_bitrate_field_value_vt,
        check_audio_bitrate_field_value,
        monitor_bitrate
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
