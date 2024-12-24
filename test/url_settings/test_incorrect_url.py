import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.notificaton_handler import NotificationHandler
from utils.urls import WEB_GUEST_PAGE_URL


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


def test_incorrect_url(driver, logger):
    @log_step(logger, "ШАГ 1. Проверка URL")
    def check_url(driver):
        expected_url = f"{WEB_GUEST_PAGE_URL}incorrect"
        driver.get(expected_url)
        current_url = driver.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    base_page = BasePage(driver)
    wg_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)
    volume_fader_value_state_off = '0'

    @log_step(logger, "ШАГ 2. Проверка значка кнопки MUTE - состояние: ВКЛ.")
    def check_mute_image_state_on():
        assert not wg_page.is_button_pressed(wg_page.MUTE_BUTTON), "Кнопка MUTE в состоянии ВЫКЛ."

    @log_step(logger, "ШАГ 3. Проверка отображения Volume Fader - состояние: ВЫКЛ.")
    def check_volume_fader_value_state_off():
        expected_value = volume_fader_value_state_off
        actual_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER)
        assert actual_value == expected_value, (f"Ожидалось значение '{expected_value}', "
                                                f"но получено '{actual_value}'")

    @log_step(logger, "ШАГ 4. Проверка отображения окна Selfie - состояние: ВКЛ")
    def check_preview_window_state_on():
        assert base_page.is_element_present(wg_page.PREVIEW_WINDOW), "Окно Selfie не отображается"

    @log_step(logger, "ШАГ 5. Проверка отображения окна - You are not authorized")
    def check_authorized_notification():
        assert notification_handler.check_notification(), "Окно You are not authorized не отображается"

    try:
        check_url(driver)
        check_authorized_notification()
        check_mute_image_state_on()
        check_volume_fader_value_state_off()
        check_preview_window_state_on()
        check_authorized_notification()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
