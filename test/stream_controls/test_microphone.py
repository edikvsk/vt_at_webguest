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


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_microphone(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    mic_on_text = "TURN OFF MICROPHONE"
    mic_off_text = "TURN ON MICROPHONE"

    vt_web_guest_source_name = "Web Guest"

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки MICROPHONE")
    def check_mic_button():
        assert base_page.is_element_present(wg_page.MICROPHONE_BUTTON), "Кнопка MICROPHONE не отображается"

    @log_step(logger, "ШАГ 2. Проверка значка кнопки MICROPHONE - состояние: ВКЛ.")
    def check_mic_image_state_on():
        assert wg_page.is_button_pressed(wg_page.MICROPHONE_BUTTON), "Кнопка камеры в состонии ВЫКЛ."

    @log_step(logger, "ШАГ 3. Проверка tooltip - текст: TURN OFF MICROPHONE")
    def check_tooltip_state_on():
        expected_text = mic_on_text
        actual_text = wg_page.get_tooltip_text(wg_page.MICROPHONE_BUTTON, wg_page.MICROPHONE_TOOLTIP)
        assert actual_text == expected_text, f"Ожидался текст подсказки '{expected_text}', но получен '{actual_text}'"

    @log_step(logger, "ШАГ 4. Отключение микрофона")
    def turn_off_mic():
        base_page.click(wg_page.MICROPHONE_BUTTON)

    @log_step(logger, "ШАГ 5. Проверка значка кнопки MICROPHONE - состояние: ВЫКЛ.")
    def check_mic_image_state_off():
        assert not wg_page.is_button_pressed(wg_page.MICROPHONE_BUTTON), "Кнопка микрофона в состонии ВКЛ."

    @log_step(logger, "ШАГ 6. Проверка tooltip - текст: TURN ON MICROPHONE")
    def check_tooltip_state_off():
        expected_text = mic_off_text
        actual_text = wg_page.get_tooltip_text(wg_page.MICROPHONE_BUTTON, wg_page.MICROPHONE_TOOLTIP)
        assert actual_text == expected_text, f"Ожидался текст подсказки '{expected_text}', но получен '{actual_text}'"

    @log_step(logger, "ШАГ 7. Проверка toggle button VT WG Settings  - состояние: ВЫКЛ.")
    def check_microphone_toggle_button_state_off():
        expected_value = 0  # Состояние кнопки (0 == False)
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        actual_value = desktop_app_page.get_vt_wg_button_state(2)
        desktop_app_page.click_button_by_name(desktop_app_page.VT_OK_BUTTON)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    try:
        check_mic_button()
        check_mic_image_state_on()
        check_tooltip_state_on()
        turn_off_mic()
        check_mic_image_state_off()
        check_tooltip_state_off()
        check_microphone_toggle_button_state_off()

    except (NoSuchElementException, TimeoutException) as e:

        logger.error(f"Ошибка при выполнении теста: {e}")

        pytest.fail(f"Ошибка при выполнении теста: {e}")

    # При необходимости закрыть VT
    # finally:

    # desktop_app.close_application()
