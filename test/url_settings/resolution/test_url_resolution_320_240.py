import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, modified_url_fixture
from utils.desktop_app import DesktopApp
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.webrtc_stream_handler import StreamHandler
from utils.urls import WEB_GUEST_PAGE_URL, PROCESS_PATH


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.parametrize("modified_url_fixture",
                         [f"{WEB_GUEST_PAGE_URL}?resolution=320x240"],
                         indirect=True)
def test_url_resolution_320_240(modified_url_fixture, driver, logger):
    @log_step(logger, "ШАГ 1. Проверка URL")
    def check_url(driver):
        expected_url = f"{WEB_GUEST_PAGE_URL}?resolution=320x240"

        current_url = driver.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    stream_handler = StreamHandler(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_web_guest_source_name = "Web Guest"
    resolution = "320X240"

    @log_step(logger, "ШАГ 2. Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "ШАГ 3. Нажатие кнопки SETTINGS")
    def click_settings_button():
        base_page.click(wg_page.SETTINGS_BUTTON)

    @log_step(logger, "ШАГ 4. Проверка значения поля Resolution")
    def check_resolution_settings():
        expected_value = resolution
        actual_value = wg_page.get_settings_item_value_text(wg_page.RESOLUTION_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 5. Проверка значения Resolution в VT WebGuest Settings")
    def check_resolution_field_value_vt():
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        desktop_app_page.select_combobox_item_by_index(0, 0)
        desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)

    @log_step(logger, "ШАГ 6. Проверка значения поля Resolution")
    def check_resolution_field_value():
        expected_value = resolution
        actual_value = wg_page.get_settings_item_value_text(wg_page.RESOLUTION_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 7. Перезапуск стрима для обновления WebRTC stats")
    def restart_streaming():
        base_page.click(wg_page.STOP_BUTTON)
        base_page.click(wg_page.START_BUTTON)
        assert wg_page.is_button_pressed(wg_page.STOP_BUTTON), "Кнопка STOP не отображается"

    @log_step(logger, "ШАГ 8. Проверка значения Resolution в WebRTC")
    def check_webrtc_frame_dimensions():
        expected_value = resolution
        actual_value = stream_handler.get_video_frame_dimensions()
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    steps = [
        lambda: check_url(driver),
        check_settings_button,
        click_settings_button,
        check_resolution_settings,
        check_resolution_field_value_vt,
        check_resolution_field_value,
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
