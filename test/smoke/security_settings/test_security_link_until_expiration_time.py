import configparser
import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.config import CONFIG_INI, PROCESS_PATH, SOURCE_TO_PUBLISHING
from utils.conftest import driver, modified_fixture
from utils.desktop_app import DesktopApp
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
def test_security_link_until_expiration_time(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)
    web_guest_url = config['DEFAULT']['WEB_GUEST_PAGE_URL'].strip()

    base_page = BasePage(driver)
    wg_page = WebGuestPage(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)
    webrtc_stream_handler = StreamHandler(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_input_source_name = SOURCE_TO_PUBLISHING
    login = "test_login"
    password = "test_password"
    expected_notification_text = "Link has expired"

    @log_step(logger, "Отключение anonymous access VT Security Settings")
    def check_vt_anonymous_access_state_on():
        expected_value = 0  # Состояние кнопки (0 == False)
        desktop_app_page.right_click_vt_source_item(vt_input_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_SECURITY_SETTINGS)
        desktop_app_page.toggle_vt_wg_button(0)
        actual_value = desktop_app_page.get_vt_wg_button_state(0)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Добавление Security Account")
    def add_security_account():
        start_time = wg_page.get_current_time_formatted()
        expiration_time = wg_page.add_time(start_time, minutes=2)
        desktop_app_page.click_button_by_name("Add")
        desktop_app_page.set_vt_wg_settings_field_value(0, login)
        desktop_app_page.set_vt_wg_settings_field_value(1, password)
        desktop_app_page.set_vt_wg_settings_field_value(3, start_time)
        desktop_app_page.set_vt_wg_settings_field_value(4, expiration_time)
        desktop_app_page.click_button_by_name("OK")

    @log_step(logger, "Запуск Web Guest")
    def start_web_guest(drv):
        drv.get(web_guest_url)
        expected_url = web_guest_url

        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

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

    @log_step(logger, "Авторизация")
    def authorization():
        wg_page.input_text(wg_page.SECURITY_LOGIN, login)
        wg_page.input_text(wg_page.SECURITY_PASSWORD, password)
        wg_page.click(wg_page.SECURITY_CONNECT_BUTTON)

    @log_step(logger, "Проверка отображения уведомлений")
    def check_authorized_notification():
        notification_handler.get_notification_text()

    @log_step(logger, "Проверка WebRTC трансляции")
    def check_webrtc_stream():
        stream_audio = webrtc_stream_handler.is_audio_stream_active()
        stream_video = webrtc_stream_handler.is_video_stream_active()
        assert stream_audio and stream_video, "WebRTC трансляция не активна: audio={} video={}".format(stream_audio,
                                                                                                       stream_video)

    @log_step(logger, "Ожидание уведомления об истечении срока действия")
    def wait_for_expired_notification(drv):
        try:
            logger.info("Ждем 2 минуты до истечения срока действия ссылки...")

            WebDriverWait(drv, 120).until(
                EC.text_to_be_present_in_element(wg_page.NOTIFICATION_ELEMENT, expected_notification_text)
            )
            logger.info("Уведомление 'Link has expired' успешно отображено.")
        except TimeoutException:
            logger.error("Уведомление 'Link has expired' не появилось в течение ожидаемого времени.")
            pytest.fail("Уведомление 'Link has expired' не появилось в течение ожидаемого времени.")

    @log_step(logger, "Удаление Security Account")
    def remove_security_account():
        security_window = desktop_app_page.find_window_by_title_substring("security settings")
        desktop_app_page.click_data_item_in_window(security_window, "VT_Common.SecurityAccount")
        desktop_app_page.click_button_by_name("Delete")

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
        add_security_account()
        start_web_guest(driver)
        check_authorization_form()
        check_name_field()
        check_location_field()
        check_login_field()
        check_password_field()
        authorization()
        check_authorized_notification()
        check_webrtc_stream()
        wait_for_expired_notification(driver)

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")

    finally:
        try:
            remove_security_account()
        except Exception as cleanup_error:
            logger.error(f"Ошибка при удалении Security Account: {cleanup_error}")

        try:
            check_vt_anonymous_access_state_off()
        except Exception as cleanup_error:
            logger.error(f"Ошибка при включении anonymous access: {cleanup_error}")
