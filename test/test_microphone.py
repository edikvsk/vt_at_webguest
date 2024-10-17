import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

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
def test_microphone(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)

    mic_off_text = "TURN OFF MICROPHONE"
    mic_on_text = "TURN ON MICROPHONE"

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки MICROPHONE")
    def check_mic_button():
        assert base_page.is_element_present(wg_page.MICROPHONE_BUTTON), "Кнопка MICROPHONE не отображается"

    @log_step(logger, "ШАГ 2. Проверка значка кнопки MICROPHONE - состояние: ВКЛ.")
    def check_mic_image_state_on():
        assert wg_page.is_button_pressed(wg_page.MICROPHONE_BUTTON), "Кнопка камеры в состонии ВЫКЛ."

    @log_step(logger, "ШАГ 3. Проверка tooltip")
    def check_tooltip(expected_text):
        actual_text = wg_page.get_tooltip_text(wg_page.MICROPHONE_BUTTON, wg_page.MICROPHONE_TOOLTIP)
        assert actual_text == expected_text, f"Ожидался текст подсказки '{expected_text}', но получен '{actual_text}'"

    @log_step(logger, "ШАГ 4. Отключение микрофона")
    def turn_off_mic():
        base_page.click(wg_page.MICROPHONE_BUTTON)

    @log_step(logger, "ШАГ 5. Проверка значка кнопки MICROPHONE - состояние: ВЫКЛ.")
    def check_mic_image_state_off():
        assert not wg_page.is_button_pressed(wg_page.MICROPHONE_BUTTON), "Кнопка микрофона в состонии ВКЛ."

    @log_step(logger, "ШАГ 6. Включение микрофона")
    def turn_on_mic():
        base_page.click(wg_page.MICROPHONE_BUTTON)

    try:
        check_mic_button()
        check_mic_image_state_on()
        check_tooltip(mic_off_text)
        turn_off_mic()
        check_tooltip(mic_on_text)
        check_mic_image_state_off()
        turn_on_mic()
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
