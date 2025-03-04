import os
import time

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
from utils.notificaton_handler import NotificationHandler
from utils.webrtc_stream_handler import StreamHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_resolution_1920x1080(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    stream_handler = StreamHandler(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_web_guest_source_name = "Web Guest"
    resolution = "1920X1080"

    @log_step(logger, "Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "Нажатие кнопки SETTINGS")
    def click_settings_button():
        base_page.click(wg_page.SETTINGS_BUTTON)
        assert wg_page.is_element_visible(wg_page.WG_SETTINGS_WINDOW), "Settings не открыты"

    @log_step(logger, "Выбор разрешения")
    def select_resolution():
        wg_page.select_resolution(resolution)
        notification_handler.check_notification()
        base_page.click(wg_page.RESOLUTION_COMBOBOX_BACK_BUTTON)
        expected_value = resolution
        actual_value = wg_page.get_settings_item_value_text(wg_page.RESOLUTION_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Проверка значения Resolution в VT WebGuest Settings")
    def check_resolution_field_value_vt():
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        desktop_app_page.select_combobox_item_by_index(0, 4)
        desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)

    @log_step(logger, "Проверка значения поля Resolution")
    def check_resolution_field_value():
        expected_value = resolution
        actual_value = wg_page.get_settings_item_value_text(wg_page.RESOLUTION_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Перезапуск стрима для обновления WebRTC stats")
    def restart_streaming():
        base_page.click(wg_page.STOP_BUTTON)
        base_page.click(wg_page.START_BUTTON)
        assert wg_page.is_button_pressed(wg_page.STOP_BUTTON), "Кнопка STOP не отображается"

    @log_step(logger, "Проверка значения Resolution в WebRTC")
    def check_webrtc_frame_dimensions():
        time.sleep(25)
        expected_value = resolution
        actual_value = stream_handler.get_video_frame_dimensions()
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    steps = [
        check_settings_button,
        click_settings_button,
        select_resolution,
        check_resolution_field_value,
        check_resolution_field_value_vt,
        click_settings_button,
        restart_streaming,
        check_webrtc_frame_dimensions
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
