import os

import pytest

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, open_web_preview_fixture
from utils.logger_config import setup_logger


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("open_web_preview_fixture")
def test_open_preview_from_context_menu_VT1626(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    assert driver.current_url.startswith(("http://", "https://")), \
        f"Preview URL не открыт: {driver.current_url}"
    assert base_page.is_element_visible(wg_page.PREVIEW_REMOTE_WINDOW, timeout=30), \
        "Remote Preview video не отображается"
