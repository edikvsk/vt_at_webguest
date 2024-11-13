import os
import time

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, login_fixture
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.process_utils import ProcessManager
from utils.urls import PROCESS_NAME, PROCESS_PATH, XML_FILE_PATH
from utils.xml_utils import XMLReader


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_name(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    process_manager = ProcessManager(PROCESS_PATH, PROCESS_NAME)
    xml_reader = XMLReader(XML_FILE_PATH, logger)

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "ШАГ 2. Нажатие кнопки SETTINGS")
    def click_settings_button():
        base_page.click(wg_page.SETTINGS_BUTTON)

    @log_step(logger, "ШАГ 3. Ввод имени")
    def input_name(name):
        wg_page.input_name(name)

    @log_step(logger, "ШАГ 4. Проверка значения поля имени")
    def check_name_field_value(expected_value):
        wg_actual_value = wg_page.get_name_field_value()
        assert wg_actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{wg_actual_value}'"
        return wg_actual_value

    @log_step(logger, "ШАГ 5. Проверка channel_label в XML")
    def check_channel_label_in_xml(expected_label):
        channel_label = xml_reader.find_channel_by_label(expected_label)  # Вызываем метод для поиска канала
        assert channel_label is not None, f"Канал с label '{expected_label}' не найден в XML."
        assert channel_label == expected_label, f"Ожидалось значение '{expected_label}', но получено '{channel_label}'."

    try:
        check_settings_button()
        click_settings_button()

        # Генерация случайного имени
        random_name = wg_page.generate_random_name()  # Используем метод генерации имени
        input_name(random_name)  # Вводим сгенерированное имя
        actual_name = check_name_field_value(random_name)  # Проверяем значение поля имени
        process_manager.kill_process()
        time.sleep(7)
        check_channel_label_in_xml(actual_name)  # Проверяем channel_label в XML

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
