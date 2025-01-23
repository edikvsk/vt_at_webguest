import os

import pytest

from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, open_web_preview_fixture
from utils.logger_config import setup_logger


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("open_web_preview_fixture")
def test_open_preview_from_context_menu(driver, logger):
    wg_page = WebGuestPage(driver)
