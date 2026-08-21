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


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("modified_fixture")
def test_url_autojoin_volume_fader_vt1420(driver, logger):
    config_file_path = CONFIG_INI
    config = configparser.ConfigParser()
    config.read(config_file_path)
    web_guest_url = config['DEFAULT']['WEB_GUEST_PAGE_URL'].strip()

    @log_step(logger, "Проверка URL")
    def check_url(drv):
        drv.get(web_guest_url + "?autojoin=1")
        expected_url = f"{web_guest_url}?autojoin=1"

        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"
        assert base_page.is_element_visible(wg_page.STOP_BUTTON, timeout=40), \
            "Autojoin не завершился за 40 секунд"

    base_page = BasePage(driver)
    wg_page = WebGuestPage(driver)

    @log_step(logger, "Проверка отображения окна Selfie - состояние: ВКЛ")
    def check_preview_window_state_on():
        assert base_page.is_element_present(wg_page.PREVIEW_WINDOW), "Окно Selfie не отображается"

    @log_step(logger, "Проверка что Volume Fader не отображается при autojoin")
    def check_volume_fader_not_visible():
        assert not base_page.is_element_visible(wg_page.VOLUME_FADER), "Volume Fader не должен отображаться при autojoin"

    @log_step(logger, "Клик по MUTE/UNMUTE и проверка появления Volume Fader")
    def toggle_mute_unmute_and_check_fader_visible():
        # Первый клик (mute или unmute)
        from selenium.webdriver.common.by import By
        from selenium.webdriver import ActionChains
        ActionChains(driver).move_to_element(driver.find_element(By.TAG_NAME, "body")).perform()
        wg_page.hover_element(wg_page.MUTE_BUTTON)
        assert base_page.click(wg_page.MUTE_BUTTON), "Не удалось кликнуть по кнопке MUTE"

        # Проверяем появление фейдера; если не появился, кликаем повторно (unmute/mute)
        if not base_page.is_element_visible(wg_page.VOLUME_FADER):
            assert base_page.click(wg_page.MUTE_BUTTON), "Не удалось повторно кликнуть по кнопке MUTE"

        assert base_page.is_element_visible(wg_page.VOLUME_FADER), "Ожидалось появление Volume Fader"

    try:
        check_url(driver)
        check_preview_window_state_on()
        check_volume_fader_not_visible()
        toggle_mute_unmute_and_check_fader_visible()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")


