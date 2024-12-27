import os

import pytest
from selenium.common.exceptions import TimeoutException
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
    "You are not authorized",
    "Overconstrained error"
]

# Определяем список уведомлений, которые не должны прерывать тест
NOTIFICATION_TO_IGNORE = [
    "Текст уведомления, которое игнорируется 1"
]


class NotificationHandler:
    def __init__(self, driver, notification_element, logger):
        self.driver = driver
        self.notification_element = notification_element
        self.logger = logger  # Сохраняем логгер

    def check_notification(self, ignore_fail_notifications=False, reason=None):
        base_page = BasePage(self.driver)
        try:
            self.logger.info("Ожидание уведомления...")
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.notification_element)
            )
            notification_text = base_page.get_text(self.notification_element)
            self.logger.warning(f"Найдено уведомление: {notification_text}")

            # Проверка на игнорируемые уведомления
            if any(word in notification_text for word in NOTIFICATION_TO_IGNORE):
                self.logger.info(f"Уведомление игнорируется: {notification_text}")
                return  # Завершаем выполнение, если уведомление игнорируется

            # Проверка на уведомления, которые прерывают тест
            if any(word in notification_text for word in NOTIFICATION_TO_FAIL):
                self.logger.info(f"Уведомление найдено в списке прерывающих: {notification_text}")
                if ignore_fail_notifications:
                    self.logger.info(f"Уведомление игнорируется: {notification_text}")
                    return  # Выход из функции, если уведомление игнорируется
                else:
                    error_message = f"Тест прерван: {notification_text}"
                    if reason:
                        error_message += f" | Дополнительная информация: {reason}"
                    self.logger.error(error_message)
                    pytest.fail(error_message)

            self.logger.info(f"Уведомление не требует действий: {notification_text}")

        except TimeoutException:
            self.logger.warning("Уведомление не найдено, продолжаем тест.")
        except Exception as e:
            self.logger.error(f"Произошла ошибка при проверке уведомления: {str(e)}")

    def get_notification_text(self, timeout=10):
        base_page = BasePage(self.driver)
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.notification_element)
            )
            return base_page.get_text(self.notification_element)
        except TimeoutException:
            message = "Уведомление не найдено в течение {} секунд.".format(timeout)
            self.logger.info(message)
            return message  # Возвращаем сообщение вместо None

    class CustomErrorFilter():
        def filter(self, record):
            if record.levelname == "ERROR":
                record.levelname = "ERROR__"
            return True
