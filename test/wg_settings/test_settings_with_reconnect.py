import os
import time

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.config import MIC_FOR_SELECTION_IN_TEST_MICROPHONE_SELECT, CAMERA_FOR_SELECTION_IN_TEST_CAMERA_SELECT
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
def test_settings_with_reconnect(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    stream_handler = StreamHandler(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_web_guest_source_name = "Web Guest"
    resolution = "320X240"
    framerate = "15 FPS"
    microphone = MIC_FOR_SELECTION_IN_TEST_MICROPHONE_SELECT
    camera = CAMERA_FOR_SELECTION_IN_TEST_CAMERA_SELECT

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

    @log_step(logger, "Проверка отображения WebGuest в VT  - состояние: ВКЛ.")
    def check_vt_webguest_state_on():
        time.sleep(5)
        assert desktop_app_page.check_element_exists_by_title_part(vt_web_guest_source_name), \
            f"Источник WebGuest не отображается в VT"

    @log_step(logger, "Выбор Framerate")
    def select_framerate():
        wg_page.select_framerate(framerate)
        notification_handler.check_notification()
        base_page.click(wg_page.COMBOBOX_BACK_BUTTON)
        expected_value = framerate
        actual_value = wg_page.get_settings_item_value_text(wg_page.FRAMERATE_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Проверка наличия аудиопотока")
    def check_audio_stream_available():
        assert stream_handler.is_audio_stream_active(), "Аудиопоток отстутствует"

    @log_step(logger, "Проверка наличия видиопотока")
    def check_video_stream_available():
        assert stream_handler.is_video_stream_active(), "Видеопоток отстутствует"

    @log_step(logger, "Выбор микрофона")
    def select_microphone():
        wg_page.select_microphone(microphone)
        notification_handler.check_notification()
        wg_page.hover_element(wg_page.RESOLUTION_COMBOBOX_BACK_BUTTON)
        wg_page.click(wg_page.RESOLUTION_COMBOBOX_BACK_BUTTON)
        expected_value = microphone
        actual_value = wg_page.get_settings_item_value_text(wg_page.INPUT_MICROPHONE_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Выбор камеры")
    def select_camera():
        wg_page.select_camera(camera)
        notification_handler.check_notification()
        wg_page.hover_element(wg_page.RESOLUTION_COMBOBOX_BACK_BUTTON)
        base_page.click(wg_page.RESOLUTION_COMBOBOX_BACK_BUTTON)
        expected_value = camera
        actual_value = wg_page.get_settings_item_value_text(wg_page.INPUT_CAMERA_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Выключение Audio Enhancements")
    def turn_off_audio_enhancements():
        wg_page.click_element_with_scroll(wg_page.AUDIO_ENHANCEMENTS_SWITCHER)

    steps = [
        check_settings_button,
        click_settings_button,
        select_resolution,
        check_vt_webguest_state_on,
        check_audio_stream_available,
        check_video_stream_available,
        select_framerate,
        check_vt_webguest_state_on,
        check_audio_stream_available,
        check_video_stream_available,
        select_microphone,
        check_vt_webguest_state_on,
        check_audio_stream_available,
        check_video_stream_available,
        select_camera,
        check_vt_webguest_state_on,
        check_audio_stream_available,
        check_video_stream_available,
        turn_off_audio_enhancements,
        check_vt_webguest_state_on,
        check_audio_stream_available,
        check_video_stream_available

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
