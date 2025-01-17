import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.web_guest_page import WebGuestPage
from utils.config import WEB_GUEST_PAGE_URL
from utils.conftest import driver, modified_url_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.parametrize("modified_url_fixture",
                         [f"{WEB_GUEST_PAGE_URL}?audio=f"],
                         indirect=True)
def test_url_audio_f(modified_url_fixture, driver, logger):
    @log_step(logger, "ШАГ 1. Проверка URL")
    def check_url(drv):
        expected_url = f"{WEB_GUEST_PAGE_URL}?audio=f"

        current_url = drv.current_url
        logger.info(f"Ожидаемый URL: {expected_url}, текущий URL: {current_url}")

        assert current_url == expected_url, f"Ожидался URL: {expected_url}, но был: {current_url}"

    wg_page = WebGuestPage(driver)
    volume_fader_value_state_off = '0'

    @log_step(logger, "ШАГ 2. Проверка значка кнопки MUTE - состояние: ВКЛ.")
    def check_mute_image_state_on():
        assert not wg_page.is_button_pressed(wg_page.MUTE_BUTTON), "Кнопка MUTE в состоянии ВЫКЛ."

    @log_step(logger, "ШАГ 3. Проверка отображения Volume Fader - состояние: ВЫКЛ.")
    def check_volume_fader_value_state_off():
        expected_value = volume_fader_value_state_off
        actual_value = wg_page.get_volume_fader_value(wg_page.VOLUME_FADER)
        assert actual_value == expected_value, (f"Ожидалось значение '{expected_value}', "
                                                f"но получено '{actual_value}'")

    try:
        check_url(driver)
        check_mute_image_state_on()
        check_volume_fader_value_state_off()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
