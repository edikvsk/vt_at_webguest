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
def test_url_audio_true(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)
    web_guest_url = config['DEFAULT']['WEB_GUEST_PAGE_URL'].strip()

    base_page = BasePage(driver)
    wg_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)

    @log_step(logger, "ШАГ 1. Проверка URL")
    def check_url(drv):
        drv.get(web_guest_url + "?audio=true")
        expected_url = f"{web_guest_url}?audio=true"

        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    wg_page = WebGuestPage(driver)
    volume_fader_value_state_on = '100'

    @log_step(logger, "ШАГ 2. Проверка Notifications")
    def check_notifications():
        assert not notification_handler.check_notification(), "Найдено блокирующее уведомление"

    @log_step(logger, "ШАГ 3. Проверка отображения Authorization Form")
    def check_authorization_form():
        assert base_page.is_element_visible(wg_page.AUTHORIZATION_FORM), "Authorization Form не отображается"

    @log_step(logger, "ШАГ 4. Логин")
    def login():
        base_page.click(wg_page.LOGIN_BUTTON)
        assert base_page.is_element_visible(wg_page.STOP_BUTTON), "Логин НЕ выполнен"

    @log_step(logger, "ШАГ 5. Проверка значка кнопки MUTE - состояние: ВЫКЛ.")
    def check_mute_image_state_off():
        assert not wg_page.is_button_pressed(wg_page.MUTE_BUTTON), "Кнопка MUTE в состоянии ВКЛ."

    @log_step(logger, "ШАГ 6. Проверка отображения Volume Fader - состояние: ВКЛ.")
    def check_volume_fader_value_state_on():
        expected_value = volume_fader_value_state_on
        actual_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER)
        assert actual_value == expected_value, (f"Ожидалось значение '{expected_value}', "
                                                f"но получено '{actual_value}'")

    try:
        check_url(driver)
        check_notifications()
        check_authorization_form()
        login()
        check_mute_image_state_off()
        check_volume_fader_value_state_on()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
