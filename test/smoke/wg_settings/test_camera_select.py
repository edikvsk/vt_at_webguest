import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.config import CAMERA_FOR_SELECTION_IN_TEST_CAMERA_SELECT
from utils.config import PROCESS_PATH
from utils.conftest import driver, login_fixture
from utils.desktop_app import DesktopApp
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.notificaton_handler import NotificationHandler


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_camera_select(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_web_guest_source_name = "Web Guest"
    camera = CAMERA_FOR_SELECTION_IN_TEST_CAMERA_SELECT

    @log_step(logger, "Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "Нажатие кнопки SETTINGS")
    def click_settings_button():
        wg_page.click_element_with_scroll(wg_page.SETTINGS_BUTTON)
        import time
        time.sleep(1)  # Небольшая задержка для открытия окна настроек
        assert wg_page.is_element_visible(wg_page.WG_SETTINGS_WINDOW), "Settings не открыты"

    @log_step(logger, "Выбор камеры")
    def select_camera():
        wg_page.select_camera(camera)
        notification_handler.check_notification()
        wg_page.hover_element(wg_page.RESOLUTION_COMBOBOX_BACK_BUTTON)
        base_page.click(wg_page.RESOLUTION_COMBOBOX_BACK_BUTTON)
        expected_value = camera
        actual_value = wg_page.get_settings_item_value_text(wg_page.INPUT_CAMERA_VALUE)
        assert expected_value.lower() in actual_value.lower(), f"Ожидался фрагмент '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "Проверка выбранной камеры в VT WebGuest Settings")
    def check_camera_field_value_vt():
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        desktop_app_page.select_combobox_item_by_name(3, camera)
        desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)

    @log_step(logger, "Проверка значения поля Camera")
    def check_camera_field_value():
        expected_value = camera
        actual_value = wg_page.get_settings_item_value_text(wg_page.INPUT_CAMERA_VALUE)
        assert expected_value.lower() in actual_value.lower(), f"Ожидался фрагмент '{expected_value}', но получено '{actual_value}'"

    steps = [
        check_settings_button,
        click_settings_button,
        select_camera,
        check_camera_field_value_vt,
        check_camera_field_value
    ]

    try:
        for step in steps:
            step()
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
    finally:
        desktop_app.close_application()
