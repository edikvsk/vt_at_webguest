import os

import pytest
from selenium.common import NoSuchElementException, TimeoutException

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
def test_camera(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)

    camera_off_text = "TURN OFF CAMERA"
    camera_on_text = "TURN ON CAMERA"

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки CAMERA")
    def check_camera_button():
        assert base_page.is_element_present(wg_page.CAMERA_BUTTON), "Кнопка CAMERA не отображается"

    @log_step(logger, "ШАГ 2. Проверка значка кнопки CAMERA - состояние: ВКЛ.")
    def check_camera_image_state_on():
        assert wg_page.is_button_pressed(wg_page.CAMERA_BUTTON), "Кнопка камеры в состонии ВЫКЛ."

    @log_step(logger, "ШАГ 3. Проверка tooltip")
    def check_tooltip(expected_text):
        actual_text = wg_page.get_tooltip_text(wg_page.CAMERA_BUTTON, wg_page.CAMERA_TOOLTIP)
        assert actual_text == expected_text, f"Ожидался текст подсказки '{expected_text}', но получен '{actual_text}'"

    @log_step(logger, "ШАГ 4. Проверка отображения окна превью камеры")
    def check_preview_window():
        assert base_page.is_element_present(wg_page.PREVIEW_WINDOW), "Окно превью камеры НЕ отображается"

    @log_step(logger, "ШАГ 5. Отключение камеры")
    def turn_off_camera():
        base_page.click(wg_page.CAMERA_BUTTON)
        assert not base_page.is_element_present(wg_page.PREVIEW_WINDOW), "Окно превью камеры все еще отображается"

    @log_step(logger, "ШАГ 6. Проверка значка кнопки CAMERA - состояние: ВЫКЛ.")
    def check_camera_image_state_off():
        assert not wg_page.is_button_pressed(wg_page.CAMERA_BUTTON), "Кнопка камеры в состонии ВКЛ."

    @log_step(logger, "ШАГ 7. Включение камеры")
    def turn_on_camera():
        base_page.click(wg_page.CAMERA_BUTTON)
        assert base_page.is_element_present(wg_page.PREVIEW_WINDOW), "Окно превью камеры НЕ отображается"

    try:
        check_camera_button()
        check_camera_image_state_on()
        check_tooltip(camera_off_text)
        check_preview_window()
        turn_off_camera()
        check_tooltip(camera_on_text)
        check_camera_image_state_off()
        turn_on_camera()
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
