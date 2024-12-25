import os
import time

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.config import MIC_FOR_SELECTION_IN_TEST_MICROPHONE_SELECT
from utils.conftest import driver, login_fixture
from utils.desktop_app import DesktopApp
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.notificaton_handler import NotificationHandler
from utils.urls import PROCESS_PATH


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_microphone_select(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_web_guest_source_name = "Web Guest"
    microphone = MIC_FOR_SELECTION_IN_TEST_MICROPHONE_SELECT

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "ШАГ 2. Нажатие кнопки SETTINGS")
    def click_settings_button():
        base_page.click(wg_page.SETTINGS_BUTTON)

    @log_step(logger, "ШАГ 3. Выбор микрофона")
    def select_microphone():
        time.sleep(3.5)
        wg_page.select_microphone(microphone)
        notification_handler.check_notification()
        wg_page.hover_element(wg_page.RESOLUTION_COMBOBOX_BACK_BUTTON)
        wg_page.click(wg_page.RESOLUTION_COMBOBOX_BACK_BUTTON)
        expected_value = microphone
        actual_value = wg_page.get_settings_item_value_text(wg_page.INPUT_MICROPHONE_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 4. Проверка выбранного микрофона в VT WebGuest Settings")
    def check_microphone_field_value_vt():
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        desktop_app_page.select_combobox_item_by_index(2, 0)
        desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)

    @log_step(logger, "ШАГ 5. Проверка значения поля Microphone")
    def check_microphone_field_value():
        expected_value = microphone
        actual_value = wg_page.get_settings_item_value_text(wg_page.INPUT_MICROPHONE_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    steps = [
        check_settings_button,
        click_settings_button,
        select_microphone,
        check_microphone_field_value_vt,
        check_microphone_field_value
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
