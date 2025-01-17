import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.config import WEB_GUEST_PAGE_URL
from utils.conftest import driver
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.notificaton_handler import NotificationHandler
from utils.webrtc_stream_handler import StreamHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


def test_login_incorrect_location(driver, logger):
    @log_step(logger, "ШАГ 1. Проверка URL")
    def check_url(drv):
        expected_url = WEB_GUEST_PAGE_URL
        drv.get(expected_url)
        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    base_page = BasePage(driver)
    wg_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)
    stream_handler = StreamHandler(driver)

    @log_step(logger, "ШАГ 2. Проверка Notifications")
    def check_notifications():
        assert not notification_handler.check_notification(), "Найдено блокирующее уведомление"

    @log_step(logger, "ШАГ 3. Проверка отображения Authorization Form")
    def check_authorization_form():
        assert base_page.is_element_visible(wg_page.AUTHORIZATION_FORM), "Authorization Form не отображается"

    @log_step(logger, "ШАГ 4. Проверка отображения поля ввода Location")
    def check_location_field():
        assert base_page.is_element_visible(wg_page.LOCATION_FIELD), "Поле Location не отображается"

    @log_step(logger, "ШАГ 5. Очистка поля ввода Location")
    def clean_location_field():
        expected_value = ""
        wg_page.delete_text(wg_page.LOCATION_FIELD)
        actual_value = wg_page.get_input_value(wg_page.LOCATION_FIELD)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 6. Логин при пустом поле Location")
    def login_empty_location_field():
        base_page.click(wg_page.LOGIN_BUTTON)
        assert base_page.is_element_visible(wg_page.AUTHORIZATION_LOCATION_FIELD_ERROR), (
            "Отсутствует сообщение об ошибке - Please provide location")

    @log_step(logger, "ШАГ 7. Проверка авторизации с пустым полем Location")
    def check_authorization_empty_location_field():
        assert not stream_handler.is_webrtc_connected(), "Трансляция началась с пустым полем Location"

    try:
        check_url(driver)
        check_notifications()
        check_authorization_form()
        check_location_field()
        clean_location_field()
        login_empty_location_field()
        check_authorization_empty_location_field()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
