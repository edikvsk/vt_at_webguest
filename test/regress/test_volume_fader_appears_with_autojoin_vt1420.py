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


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("modified_fixture")
def test_volume_fader_appears_with_autojoin_vt1420(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)
    web_guest_url = config['DEFAULT']['WEB_GUEST_PAGE_URL'].strip()

    @log_step(logger, "Проверка URL")
    def check_url(drv):
        drv.get(web_guest_url + "?autojoin=1")
        expected_url = f"{web_guest_url}?autojoin=1"

        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    base_page = BasePage(driver)
    wg_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)

    @log_step(logger, "Проверка Notifications")
    def check_notifications():
        assert not notification_handler.check_notification(), "Найдено блокирующее уведомление"

    @log_step(logger, "Проверка отображения Authorization Form")
    def check_authorization_form():
        assert not base_page.is_element_visible(wg_page.AUTHORIZATION_FORM), "Authorization Form отображается"

    @log_step(logger, "Проверка отображения окна Selfie - состояние: ВКЛ")
    def check_preview_window_state_on():
        assert base_page.is_element_present(wg_page.PREVIEW_WINDOW), "Окно Selfie не отображается"

    @log_step(logger, "Проверка отображения Volume Fader")
    def check_volume_fader_value():
        if not base_page.is_element_visible(wg_page.STOP_BUTTON):
            if base_page.is_element_visible(wg_page.VOLUME_FADER):
                assert False, "Volume Fader не должен отображаться"

    try:
        check_url(driver)
        check_notifications()
        check_authorization_form()
        check_preview_window_state_on()
        check_volume_fader_value()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
