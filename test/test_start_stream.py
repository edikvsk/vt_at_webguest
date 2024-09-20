import os

import pytest
from selenium.common import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, login_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.stream_handler import StreamHandler


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

    @log_step(logger, "ШАГ 5. Остановка трансляции")
    def turn_off_stream():
        base_page.click(wg_page.STOP_BUTTON)

    @log_step(logger, "ШАГ 6. Проверка отсутствия аудиопотока")
    def check_audio_stream_unavailable():
        assert not stream_handler.is_audio_stream_active(), "Присутствует аудиопоток"

    @log_step(logger, "ШАГ 7. Проверка наличия видеопотока")
    def check_video_stream_unavailable():
        assert not stream_handler.is_video_stream_active(), "Видеопоток отстутствует"

    @log_step(logger, "ШАГ 8. Проверка значка кнопки START")
    def check_start_button_image():
        assert wg_page.is_button_pressed(wg_page.START_BUTTON), "Кнопка START не отображается"

    @log_step(logger, "ШАГ 9. Включение трансляции")
    def turn_on_stream():
        base_page.click(wg_page.START_BUTTON)

    try:
        check_stop_button()
        check_audio_stream_available()
        check_video_stream_available()
        check_stop_button_image()
        turn_off_stream()
        check_audio_stream_unavailable()
        check_video_stream_unavailable()
        check_start_button_image()
        turn_on_stream()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
