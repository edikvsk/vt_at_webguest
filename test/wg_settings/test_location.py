import os

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


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_location(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    location_value = "01TEST_LOCATION"
    vt_web_guest_source_location = "01TEST_LOCATION"

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "ШАГ 2. Нажатие кнопки SETTINGS")
    def click_settings_button():
        base_page.click(wg_page.SETTINGS_BUTTON)
        assert wg_page.is_element_visible(wg_page.WG_SETTINGS_WINDOW), "Settings не открыты"

    @log_step(logger, "ШАГ 3. Ввод Location")
    def input_location():
        wg_page.input_text(wg_page.LOCATION_FIELD_SETTINGS, location_value)

    @log_step(logger, "ШАГ 4. Проверка значения поля Location")
    def check_location_field_value():
        expected_value = location_value
        actual_value = wg_page.get_input_value(wg_page.LOCATION_FIELD_SETTINGS)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 5. Проверка значений поля Location в VT WebGuest Settings")
    def check_location_field_vt():
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_location)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        expected_value = vt_web_guest_source_location
        actual_value = desktop_app_page.get_vt_wg_settings_field_value(1)
        desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)
        assert actual_value == expected_value, (f"Значение поля не совпадает: ожидаемое '{expected_value}', "
                                                f"полученное '{actual_value}'")

    steps = [
        check_settings_button,
        click_settings_button,
        input_location,
        check_location_field_value,
        check_location_field_vt
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
