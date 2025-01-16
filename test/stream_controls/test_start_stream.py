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
from utils.urls import PROCESS_PATH
from utils.webrtc_stream_handler import StreamHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_start_stream(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    stream_handler = StreamHandler(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_web_guest_source_name = "Web Guest"

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки STOP")
    def check_stop_button():
        assert base_page.is_element_present(wg_page.STOP_BUTTON), "Кнопка STOP не отображается"

    @log_step(logger, "ШАГ 2. Проверка наличия аудиопотока")
    def check_audio_stream_available():
        assert stream_handler.is_audio_stream_active(), "Аудиопоток отстутствует"

    @log_step(logger, "ШАГ 3. Проверка наличия видиопотока")
    def check_video_stream_available():
        assert stream_handler.is_video_stream_active(), "Видеопоток отстутствует"

    @log_step(logger, "ШАГ 4. Проверка значка кнопки STOP")
    def check_stop_button_image():
        assert wg_page.is_button_pressed(wg_page.STOP_BUTTON), "Кнопка STOP не отображается"

    @log_step(logger, "ШАГ 5. Проверка отображения WebGuest в VT  - состояние: ВКЛ.")
    def check_vt_webguest_state_on():
        assert desktop_app_page.check_element_exists_by_title_part(vt_web_guest_source_name), \
            f"Источник WebGuest не отображается в VT"

    @log_step(logger, "ШАГ 6. Остановка трансляции")
    def turn_off_stream():
        base_page.click(wg_page.STOP_BUTTON)

    @log_step(logger, "ШАГ 7. Проверка отсутствия аудиопотока")
    def check_audio_stream_unavailable():
        assert not stream_handler.is_audio_stream_active(), "Присутствует аудиопоток"

    @log_step(logger, "ШАГ 8. Проверка отсутствия видеопотока")
    def check_video_stream_unavailable():
        assert not stream_handler.is_video_stream_active(), "Присутствует видеопоток"

    @log_step(logger, "ШАГ 9. Проверка значка кнопки START")
    def check_start_button_image():
        assert wg_page.is_button_pressed(wg_page.START_BUTTON), "Кнопка START не отображается"

    @log_step(logger, "ШАГ 10. Проверка отображения WebGuest в VT  - состояние: ВЫКЛ.")
    def check_vt_webguest_state_off():
        time.sleep(10)
        assert not desktop_app_page.check_element_exists_by_title_part(vt_web_guest_source_name), \
            f"Источник WebGuest отображается в VT"

    steps = [
        check_stop_button,
        check_audio_stream_available,
        check_video_stream_available,
        check_stop_button_image,
        check_vt_webguest_state_on,
        turn_off_stream,
        check_audio_stream_unavailable,
        check_video_stream_unavailable,
        check_start_button_image,
        check_vt_webguest_state_off
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
