import os

import pytest
from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.base_page import BasePage
from utils.logger_config import setup_logger


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


# Определяем список уведомлений, которые должны прерывать тест
NOTIFICATION_TO_FAIL = [
    "You are not authorized"
]

# Определяем список уведомлений, которые не должны прерывать тест
NOTIFICATION_TO_IGNORE = [
    "Текст уведомления, которое игнорируется 1",  # Замените на текст уведомления, которое игнорируется
    "Текст уведомления, которое игнорируется 2"  # Замените на текст уведомления, которое игнорируется
]


class NotificationHandler:
    def __init__(self, driver, notification_element, logger):
        self.driver = driver
        self.notification_element = notification_element
        self.logger = logger  # Сохраняем логгер

    def check_notification(self):
        base_page = BasePage(self.driver)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.notification_element)
            )
            notification_text = base_page.get_text(self.notification_element)
            self.logger.warning(f"Найдено уведомление: {notification_text}")

            if any(word in notification_text for word in NOTIFICATION_TO_FAIL):
                pytest.fail(f"Тест прерван: {notification_text}")
            elif any(word in notification_text for word in NOTIFICATION_TO_IGNORE):
                self.logger.info(f"Уведомление игнорируется: {notification_text}")
            else:
                self.logger.info(f"Уведомление не требует действий: {notification_text}")

        except TimeoutException:
            self.logger.info("Уведомление не найдено, продолжаем тест.")
