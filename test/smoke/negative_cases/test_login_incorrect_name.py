import configparser
import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.config import CONFIG_INI
from utils.conftest import driver, modified_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.notificaton_handler import NotificationHandler
from utils.webrtc_stream_handler import StreamHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("modified_fixture")
def test_login_incorrect_name(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)
    web_guest_url = config['DEFAULT']['WEB_GUEST_PAGE_URL'].strip()

    @log_step(logger, "Проверка URL")
    def check_url(drv):
        drv.get(web_guest_url)
        expected_url = web_guest_url

        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    base_page = BasePage(driver)
    wg_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)
    stream_handler = StreamHandler(driver)

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

    @log_step(logger, "Логин при пустом поле Name")
    def login_empty_name_field():
        base_page.click(wg_page.LOGIN_BUTTON)
        assert base_page.is_element_visible(wg_page.AUTHORIZATION_NAME_FIELD_ERROR), ("Отсутствует сообщение об ошибке "
                                                                                      "- Please provide name")

    @log_step(logger, "Проверка авторизации с пустым полем Name")
    def check_authorization_empty_name_field():
        assert not stream_handler.is_webrtc_connected(), "Трансляция началась с пустым полем Name"

    try:
        check_url(driver)
        check_notifications()
        check_authorization_form()
        check_name_field()
        clean_name_field()
        login_empty_name_field()
        check_authorization_empty_name_field()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
