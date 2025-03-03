import configparser
import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.config import CONFIG_INI, PROCESS_PATH, SOURCE_TO_PUBLISHING
from utils.conftest import driver, modified_fixture
from utils.desktop_app import DesktopApp
from utils.helpers import log_step
from utils.logger_config import setup_logger


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("modified_fixture")
def test_add_new_security_account(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)

    wg_page = WebGuestPage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_input_source_name = SOURCE_TO_PUBLISHING
    login = "test_login"
    password = "test_password"

    @log_step(logger, "Отключение anonymous access VT Security Settings")
    def check_vt_anonymous_access_state_on():
        expected_value = 0  # Состояние кнопки (0 == False)
        desktop_app_page.right_click_vt_source_item(vt_input_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_SECURITY_SETTINGS)
        desktop_app_page.toggle_vt_wg_button(0)
        actual_value = desktop_app_page.get_vt_wg_button_state(0)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Добавление Security Account")
    def add_security_account():
        start_time = wg_page.get_current_time_formatted()
        expiration_time = wg_page.add_time(start_time, hours=5)
        desktop_app_page.click_button_by_name("Add")
        desktop_app_page.set_vt_wg_settings_field_value(0, login)
        desktop_app_page.set_vt_wg_settings_field_value(1, password)
        desktop_app_page.set_vt_wg_settings_field_value(2, 2)
        desktop_app_page.set_vt_wg_settings_field_value(3, start_time)
        desktop_app_page.set_vt_wg_settings_field_value(4, expiration_time)
        desktop_app_page.click_button_by_name("OK")

    @log_step(logger, "Удаление Security Account")
    def remove_security_account():
        security_window = desktop_app_page.find_window_by_title_substring("security settings")
        desktop_app_page.click_data_item_in_window(security_window, "VT_Common.SecurityAccount")
        desktop_app_page.click_button_by_name("Delete")

    @log_step(logger, "Включение anonymous access VT Security Settings")
    def check_vt_anonymous_access_state_off():
        expected_value = 1  # Состояние кнопки (1 == True)
        desktop_app_page.toggle_vt_wg_button(0)
        security_window = desktop_app_page.find_window_by_title_substring("security settings")
        actual_value = desktop_app_page.get_vt_wg_button_state(0)
        desktop_app_page.click_button_in_window(security_window, "PART_Close")
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    try:
        check_vt_anonymous_access_state_on()
        add_security_account()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")

    finally:
        try:
            remove_security_account()
        except Exception as cleanup_error:
            logger.error(f"Ошибка при удалении Security Account: {cleanup_error}")

        try:
            check_vt_anonymous_access_state_off()
        except Exception as cleanup_error:
            logger.error(f"Ошибка при включении anonymous access: {cleanup_error}")
