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
from utils.webrtc_stream_handler import StreamHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("modified_fixture")
def test_connection_with_the_same_name(driver, isolated_driver_factory, logger):
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
    stream_handler = StreamHandler(driver)
    # A separate profile prevents identity/session reuse. Fake media keeps the
    # second guest independent of the workstation's single-client camera; the
    # behavior under test is server-side duplicate-name validation.
    second_driver = isolated_driver_factory(use_fake_media=True)
    second_base_page = BasePage(second_driver)
    second_wg_page = WebGuestPage(second_driver)
    second_notification_handler = NotificationHandler(
        second_driver,
        second_wg_page.NOTIFICATION_ELEMENT,
        logger,
    )

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
        stream_handler.wait_for_webrtc_connection(timeout=40)
        # Keep the first media/signalling session alive. Stopping its tracks
        # makes WebGuest disconnect and turns the duplicate-name check into a
        # normal second connection.

    @log_step(logger, "Запуск второго экземпляра Chrome Web Guest")
    def start_second_web_guest():
        expected_url = web_guest_url
        second_driver.get(expected_url)
        current_url = second_driver.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    @log_step(logger, "Ожидание формы авторизации на второй вкладке")
    def wait_for_second_tab_form():
        assert second_base_page.is_element_visible(
            second_wg_page.AUTHORIZATION_FORM,
            timeout=60,
        ), "Authorization Form не отображается во втором изолированном браузере"

    @log_step(logger, "Ввод имени на второй вкладке")
    def set_second_web_guest_name():
        second_wg_page.delete_text(second_wg_page.LOGIN_FIELD)
        expected_value = "example"
        second_wg_page.input_text(second_wg_page.LOGIN_FIELD, "example")
        actual_value = second_wg_page.get_input_value(second_wg_page.LOGIN_FIELD)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Логин второй вкладки и проверка Connectivity Error")
    def login_second_web_guest_expect_error():
        second_base_page.click(second_wg_page.LOGIN_BUTTON)
        notification_text = second_notification_handler.get_notification_text(timeout=20)
        if notification_text and expected_notification_text in notification_text:
            logger.info(f"Получено ожидаемое уведомление: {notification_text}")
        elif notification_text and any(
            marker in notification_text
            for marker in (
                "Overconstrained error",
                "Unable to get local media stream",
                "Timeout starting video source",
            )
        ):
            pytest.skip(
                "Сценарий дублирующего имени заблокирован локальным media-device "
                f"precondition: {notification_text}"
            )
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
        start_second_web_guest()
        wait_for_second_tab_form()
        set_second_web_guest_name()
        login_second_web_guest_expect_error()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
