import configparser
import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.config import CONFIG_INI, PROCESS_PATH, SOURCE_TO_PUBLISHING
from utils.conftest import driver, modified_fixture
from utils.desktop_app import DesktopApp
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.notificaton_handler import NotificationHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("modified_fixture")
def test_allow_anonymous_access_off(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)
    web_guest_url = config['DEFAULT']['WEB_GUEST_PAGE_URL'].strip()

    base_page = BasePage(driver)
    wg_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_input_source_name = SOURCE_TO_PUBLISHING

    @log_step(logger, "Отключение anonymous access VT Security Settings")
    def check_vt_anonymous_access_state_on():
        expected_value = 0  # Состояние кнопки (0 == False)
        desktop_app_page.right_click_vt_source_item(vt_input_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_SECURITY_SETTINGS)
        desktop_app_page.toggle_vt_wg_button(0)
        actual_value = desktop_app_page.get_vt_wg_button_state(0)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Запуск первого экземпляра WG")
    def start_first_web_guest(drv):
        drv.get(web_guest_url)
        expected_url = web_guest_url

        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    @log_step(logger, "Проверка Notifications")
    def check_notifications():
        assert not notification_handler.check_notification(), "Найдено блокирующее уведомление"

    @log_step(logger, "Проверка отображения Authorization Form")
    def check_authorization_form():
        assert base_page.is_element_visible(wg_page.AUTHORIZATION_FORM), "Authorization Form не отображается"

    @log_step(logger, "Проверка отображения поля ввода Name")
    def check_name_field():
        assert base_page.is_element_visible(wg_page.SECURITY_NAME), "Поле Name не отображается"

    @log_step(logger, "Проверка отображения поля ввода Location")
    def check_location_field():
        assert base_page.is_element_visible(wg_page.SECURITY_LOCATION), "Поле Location не отображается"

    @log_step(logger, "Проверка отображения поля ввода Login")
    def check_login_field():
        assert base_page.is_element_visible(wg_page.SECURITY_LOGIN), "Поле Login не отображается"

    @log_step(logger, "Проверка отображения поля ввода Password")
    def check_password_field():
        assert base_page.is_element_visible(wg_page.SECURITY_PASSWORD), "Поле Password не отображается"

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
        start_first_web_guest(driver)
        check_notifications()
        check_authorization_form()
        check_name_field()
        check_location_field()
        check_login_field()
        check_password_field()
        check_vt_anonymous_access_state_off()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
