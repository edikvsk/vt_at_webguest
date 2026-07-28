import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.desktop_app_page import DesktopAppPage
from utils.config import PROCESS_PATH, SOURCE_TO_PUBLISHING
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
def test_allow_anonymous_access_on(driver, logger):
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_input_source_name = SOURCE_TO_PUBLISHING

    @log_step(logger, "Проверка anonymous access VT Security Settings  - состояние: ВКЛ.")
    def check_vt_anonymous_access_state_on():
        expected_value = 1  # Состояние кнопки (1 == True)
        desktop_app_page.right_click_vt_source_item(vt_input_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_SECURITY_SETTINGS)
        security_window = desktop_app_page.find_window_by_title_substring("security settings")
        actual_value = desktop_app_page.get_vt_wg_button_state(0)
        desktop_app_page.click_button_in_window(security_window, "PART_Close")
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    steps = [
        check_vt_anonymous_access_state_on
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
