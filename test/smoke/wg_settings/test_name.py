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
def test_name_field(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    name_value = "01TEST_NAME"
    vt_web_guest_source_name = "01TEST_NAME"

    @log_step(logger, "Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "Нажатие кнопки SETTINGS")
    def click_settings_button():
        base_page.click(wg_page.SETTINGS_BUTTON)
        assert wg_page.is_element_visible(wg_page.WG_SETTINGS_WINDOW), "Settings не открыты"

    @log_step(logger, "Ввод имени")
    def input_name():
        wg_page.input_text(wg_page.NAME_FIELD_SETTINGS, name_value)

    @log_step(logger, "Проверка значения поля имени")
    def check_name_field_value():
        expected_value = name_value
        actual_value = wg_page.get_input_value(wg_page.NAME_FIELD_SETTINGS)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Проверка значения поля Name в VT WebGuest Settings")
    def check_name_field_vt():
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        expected_value = vt_web_guest_source_name
        actual_value = desktop_app_page.get_vt_wg_settings_field_value(0)
        desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)
        assert actual_value == expected_value, (f"Значение поля не совпадает: ожидаемое '{expected_value}', "
                                                f"полученное '{actual_value}'")

    steps = [
        check_settings_button,
        click_settings_button,
        input_name,
        check_name_field_value,
        check_name_field_vt
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
