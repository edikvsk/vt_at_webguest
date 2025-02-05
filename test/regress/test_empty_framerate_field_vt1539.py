import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, login_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.notificaton_handler import NotificationHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_empty_framerate_field_vt1539(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)

    framerate = "60 FPS"

    @log_step(logger, "Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "Нажатие кнопки SETTINGS")
    def click_settings_button():
        wg_page.click_element_with_scroll(wg_page.SETTINGS_BUTTON)
        assert wg_page.is_element_visible(wg_page.WG_SETTINGS_WINDOW), "Settings не открыты"

    @log_step(logger, "Проверка отображения установленного Framerate")
    def select_framerate():
        wg_page.select_framerate(framerate)
        notification_handler.check_notification(ignore_fail_notifications=True)
        base_page.click(wg_page.COMBOBOX_BACK_BUTTON)
        expected_value = framerate
        actual_value = wg_page.get_settings_item_value_text(wg_page.FRAMERATE_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    steps = [
        check_settings_button,
        click_settings_button,
        select_framerate
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
