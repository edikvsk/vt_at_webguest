import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.config import PROCESS_PATH
from utils.conftest import driver, login_fixture
from utils.desktop_app import DesktopApp
from utils.helpers import log_step
from utils.logger_config import setup_logger


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_source_name_location_remain_unchanged_vt1481(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    name_value = "01TEST_NAME"
    location_value = "01TEST_LOCATION"
    vt_web_guest_source_name = "01TEST_NAME"
    vt_web_guest_source_location = "01TEST_LOCATION"
    source_title_before_update = None

    @log_step(logger, "Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"



    @log_step(logger, "Ввод Location")
    def input_location():
        # Location does not rename the connected VT row, so commit it before
        # opening the native settings dialog.  Changing Name first replaces
        # that row and makes UIA discovery race the WPF re-render.
        wg_page.input_text(wg_page.LOCATION_FIELD_SETTINGS, location_value)

    @log_step(logger, "Ввод имени")
    def input_name():
        # The already-open VT dialog receives Name updates live and gives us
        # a stable native control to validate after the source row is renamed.
        wg_page.input_text(wg_page.NAME_FIELD_SETTINGS, name_value)

    @log_step(logger, "Проверка значения поля имени")
    def check_name_and_location_field_value():
        expected = {
            'name': name_value,
            'location': location_value
        }
        actual = {
            'name': wg_page.get_input_value(wg_page.NAME_FIELD_SETTINGS),
            'location': wg_page.get_input_value(wg_page.LOCATION_FIELD_SETTINGS)
        }
        assert actual == expected, f"Ожидалось: {expected}, но получено: {actual}"

    @log_step(logger, "Открытие VT WebGuest Settings для подключенного гостя")
    def open_vt_web_guest_settings():
        desktop_app_page.right_click_vt_source_item_by_any_title(
            (source_title_before_update, "WebGuest", "Web Guest"),
            timeout=20,
        )
        desktop_app_page.click_vt_source_item(
            DesktopAppPage.VT_WEB_GUEST_SETTINGS
        )

    @log_step(logger, "Проверка значения полей Name и Location в VT WebGuest Settings")
    def check_name_and_location_field_vt():
        # The native dialog was opened while the connected row still had its
        # original caption. Validate its live values after the browser-side
        # Name update replaces that row in VT.
        expected_values = {
            'Name': (0, vt_web_guest_source_name),
            'Location': (1, vt_web_guest_source_location)
        }

        try:
            for field, (index, expected) in expected_values.items():
                actual = desktop_app_page.get_vt_wg_settings_field_value(index)
                assert actual == expected, f"{field}: ожидалось '{expected}', получено '{actual}'"
        finally:
            desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)

    @log_step(logger, "Нажатие кнопки SETTINGS")
    def click_settings_button():
        nonlocal source_title_before_update
        wg_page.click_element_with_scroll(wg_page.SETTINGS_BUTTON)
        assert wg_page.is_element_visible(wg_page.WG_SETTINGS_WINDOW), "Settings не открыты"
        source_title_before_update = wg_page.get_input_value(
            wg_page.NAME_FIELD_SETTINGS
        )

    steps = [
        check_settings_button,
        click_settings_button,
        input_location,
        open_vt_web_guest_settings,
        input_name,
        check_name_and_location_field_value,
        check_name_and_location_field_vt
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
