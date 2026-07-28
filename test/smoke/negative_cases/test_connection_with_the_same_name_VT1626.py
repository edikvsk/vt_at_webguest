import configparser
import os
import time

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.config import CONFIG_INI
from utils.conftest import driver, modified_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.notificaton_handler import NotificationHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("modified_fixture")
def test_connection_with_the_same_name(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)
    web_guest_url = config['DEFAULT']['WEB_GUEST_PAGE_URL'].strip()

    @log_step(logger, "Запуск первого экземпляра WG")
    def start_first_web_guest(drv):
        drv.get(web_guest_url)
        expected_url = web_guest_url

        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    base_page = BasePage(driver)
    wg_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)

    expected_notification_text = "Connectivity Error"

    @log_step(logger, "Проверка Notifications")
    def check_notifications():
        assert not notification_handler.check_notification(), "Найдено блокирующее уведомление"

    @log_step(logger, "Проверка отображения Authorization Form")
    def check_authorization_form():
        assert base_page.is_element_visible(wg_page.AUTHORIZATION_FORM), "Authorization Form не отображается"

    @log_step(logger, "Проверка отображения поля ввода Name")
    def check_name_field():
        assert base_page.is_element_visible(wg_page.LOGIN_FIELD), "Поле Name не отображается"

    @log_step(logger, "Очистка поля ввода Name")
    def clean_name_field():
        expected_value = ""
        wg_page.delete_text(wg_page.LOGIN_FIELD)
        actual_value = wg_page.get_input_value(wg_page.LOGIN_FIELD)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Ввод значения в поле Name для первого экземпляра Chrome Web Guest")
    def set_first_web_guest_name():
        expected_value = "example"
        wg_page.input_text(wg_page.LOGIN_FIELD, "example")
        actual_value = wg_page.get_input_value(wg_page.LOGIN_FIELD)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Логин")
    def login_first_web_guest():
        base_page.click(wg_page.LOGIN_BUTTON)
        assert base_page.is_element_visible(wg_page.STOP_BUTTON), "Логин НЕ выполнен"

    first_window = driver.current_window_handle
    logger.info(f"Дескриптор второго окна: {first_window}")

    @log_step(logger, "Запуск второго экземпляра Chrome Web Guest")
    def start_second_web_guest(drv):
        drv.execute_script("window.open('');")
        drv.switch_to.window(drv.window_handles[1])  # Переключаемся на новое окно
        time.sleep(1.5)
        expected_url = web_guest_url
        drv.get(expected_url)
        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    @log_step(logger, "Ожидание формы авторизации на второй вкладке")
    def wait_for_second_tab_form():
        assert base_page.is_element_visible(wg_page.AUTHORIZATION_FORM, timeout=180), \
            "Authorization Form не отображается на второй вкладке"

    @log_step(logger, "Ввод имени на второй вкладке")
    def set_second_web_guest_name():
        wg_page.delete_text(wg_page.LOGIN_FIELD)
        expected_value = "example"
        wg_page.input_text(wg_page.LOGIN_FIELD, "example")
        actual_value = wg_page.get_input_value(wg_page.LOGIN_FIELD)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Логин второй вкладки и проверка Connectivity Error")
    def login_second_web_guest_expect_error():
        base_page.click(wg_page.LOGIN_BUTTON)
        notification_text = notification_handler.get_notification_text(timeout=20)
        if notification_text and expected_notification_text in notification_text:
            logger.info(f"Получено ожидаемое уведомление: {notification_text}")
        else:
            pytest.fail(f"Ожидалось '{expected_notification_text}', но получено: '{notification_text}'")

    try:
        start_first_web_guest(driver)
        check_notifications()
        check_authorization_form()
        check_name_field()
        clean_name_field()
        set_first_web_guest_name()
        login_first_web_guest()
        start_second_web_guest(driver)
        wait_for_second_tab_form()
        set_second_web_guest_name()
        login_second_web_guest_expect_error()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
