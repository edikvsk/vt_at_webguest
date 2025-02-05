import configparser
import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.config import CONFIG_INI
from utils.conftest import driver, web_preview_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.notificaton_handler import NotificationHandler
from utils.webrtc_stream_handler import StreamHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("web_preview_fixture")
def test_preview_url_from_context_menu(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)
    web_preview_url = config['DEFAULT']['WEB_PREVIEW_PAGE_URL'].strip()

    base_page = BasePage(driver)
    wg_page = WebGuestPage(driver)
    stream_handler = StreamHandler(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)

    @log_step(logger, "Проверка URL")
    def check_url(drv):
        drv.get(web_preview_url)
        expected_url = web_preview_url

        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    wg_page = WebGuestPage(driver)
    volume_fader_value_state_off = '0'

    @log_step(logger, "Проверка Notifications")
    def check_notifications():
        assert not notification_handler.check_notification(), "Найдено блокирующее уведомление"

    @log_step(logger, "Проверка отображения Authorization Form")
    def check_authorization_form():
        assert base_page.is_element_visible(wg_page.AUTHORIZATION_FORM), "Authorization Form не отображается"

    @log_step(logger, "Логин")
    def login():
        assert base_page.is_element_visible(wg_page.LOGIN_BUTTON), "Логин НЕ выполнен"
        base_page.click(wg_page.LOGIN_BUTTON)

    @log_step(logger, "Проверка значка кнопки MUTE - состояние: ВКЛ.")
    def check_mute_image_state_on():
        assert not wg_page.is_button_pressed(wg_page.MUTE_BUTTON), "Кнопка MUTE в состоянии ВЫКЛ."

    @log_step(logger, "Проверка отображения Volume Fader - состояние: ВЫКЛ.")
    def check_volume_fader_value_state_off():
        expected_value = volume_fader_value_state_off
        actual_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER)
        assert actual_value == expected_value, (f"Ожидалось значение '{expected_value}', "
                                                f"но получено '{actual_value}'")

    @log_step(logger, "Проверка трансляция WebRTC")
    def check_webrtc_stream():
        assert stream_handler.wait_for_webrtc_connection(timeout=10)
        logger.info("Стрим запущен")

    try:
        check_url(driver)
        check_notifications()
        check_authorization_form()
        login()
        check_mute_image_state_on()
        check_volume_fader_value_state_off()
        check_webrtc_stream()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
