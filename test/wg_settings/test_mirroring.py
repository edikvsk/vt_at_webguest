import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, login_fixture
from utils.desktop_app import DesktopApp
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.urls import PROCESS_PATH


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_mirroring(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_web_guest_source_name = "Web Guest"

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "ШАГ 2. Нажатие кнопки SETTINGS")
    def click_settings_button():
        base_page.click(wg_page.SETTINGS_BUTTON)

    @log_step(logger, "ШАГ 3. Проверка MIRRORING Switcher - состояние: ВЫКЛ. ")
    def check_mirroring_switcher_state_off():
        assert not wg_page.is_switcher_active(wg_page.MIRRORING_SWITCHER), "Mirroring Switcher в состоянии ВКЛ."

    @log_step(logger, "ШАГ 4. Включение Mirroring")
    def turn_on_mirroring():
        wg_page.click_element_with_scroll(wg_page.MIRRORING_SWITCHER)

    @log_step(logger, "ШАГ 5. Проверка MIRRORING Switcher - состояние: ВКЛ. ")
    def check_mirroring_switcher_state_on():
        assert wg_page.is_switcher_active(wg_page.MIRRORING_SWITCHER), "Mirroring Switcher в состоянии ВЫКЛ."

    @log_step(logger, "ШАГ 6. Проверка MIRRORING switcher VT WG Settings  - состояние: ВКЛ.")
    def check_vt_wg_mirroring_switcher_state_on():
        expected_value = 1  # Состояние кнопки (1 == True)
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        actual_value = desktop_app_page.get_vt_wg_button_state(0)
        desktop_app_page.click_button_by_name(desktop_app_page.VT_OK_BUTTON)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    steps = [
        check_settings_button,
        click_settings_button,
        check_mirroring_switcher_state_off,
        turn_on_mirroring,
        check_mirroring_switcher_state_on,
        check_vt_wg_mirroring_switcher_state_on
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
