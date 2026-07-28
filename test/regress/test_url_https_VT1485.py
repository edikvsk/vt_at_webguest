import configparser
import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from utils.config import CONFIG_INI
from utils.conftest import driver, modified_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("modified_fixture")
def test_url_https_vt1485(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)
    web_guest_url = config['DEFAULT']['WEB_GUEST_PAGE_URL'].strip()

    @log_step(logger, "Проверка, что URL использует HTTPS")
    def check_url(drv):
        drv.get(web_guest_url)
        current_url = drv.current_url
        logger.info(f"Текущий URL: {current_url}")

        # Проверяем, что URL начинается с 'https'
        assert current_url.startswith("https"), f"URL должен начинаться с 'https', но был: {current_url}"

    try:
        check_url(driver)

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
