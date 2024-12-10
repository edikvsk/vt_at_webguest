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
from utils.stream_handler import StreamHandler
from utils.urls import PROCESS_PATH


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_video_bitrate_0_5m(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    stream_handler = StreamHandler(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_web_guest_source_name = "Web Guest"
    video_bitrate = "VIDEO BITRATE\n0.5M"

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "ШАГ 2. Нажатие кнопки SETTINGS")
    def click_settings_button():
        wg_page.click_element_with_scroll(wg_page.SETTINGS_BUTTON)

    @log_step(logger, "ШАГ 3. Выбор Video Bitrate")
    def select_video_bitrate():
        wg_page.select_video_bitrate(video_bitrate)
        base_page.click(wg_page.COMBOBOX_BACK_BUTTON)
        expected_value = video_bitrate
        actual_value = wg_page.get_settings_item_value_text(wg_page.VIDEO_BITRATE_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 4. Проверка значения Video Bitrate в VT WebGuest Settings")
    def check_video_bitrate_field_value_vt():
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        desktop_app_page.select_combobox_item_by_index(4, 0)
        desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)

    @log_step(logger, "ШАГ 5. Проверка значения поля Video Bitrate")
    def check_video_bitrate_field_value():
        expected_value = video_bitrate
        actual_value = wg_page.get_settings_item_value_text(wg_page.VIDEO_BITRATE_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 6. Запуск мониторинга битрейта")
    def monitor_bitrate():
        result = stream_handler.start_monitoring_video_bitrate()
        average_bitrate = result['averageVideo']
        max_bitrate = result['maxVideo']

        logger.info(f'Average Video Bitrate: {average_bitrate} Mb/s')
        logger.info(f'Max Video Bitrate: {max_bitrate} Mb/s')

    steps = [
        check_settings_button,
        click_settings_button,
        select_video_bitrate,
        check_video_bitrate_field_value_vt,
        check_video_bitrate_field_value,
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
