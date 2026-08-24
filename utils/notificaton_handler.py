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
    "Connectivity Error",
    "Link is pending activation",
    "Unable"
]

# Определяем список уведомлений, которые не должны прерывать тест
NOTIFICATION_TO_IGNORE = [
    "Текст уведомления, которое игнорируется 1"
]


class NotificationHandler:
    ABSENCE_CHECK_TIMEOUT = 2
    POLL_FREQUENCY = 0.1

    def __init__(self, driver, notification_element, logger):
        self.driver = driver
        self.notification_element = notification_element
        self.logger = logger  # Сохраняем логгер

    def check_notification(
        self,
        ignore_fail_notifications=False,
        reason=None,
        timeout=ABSENCE_CHECK_TIMEOUT,
    ):
        """Return a visible notification without imposing a 10-second absence delay."""
        base_page = BasePage(self.driver)
        try:
            self.logger.info("Ожидание уведомления...")
            WebDriverWait(
                self.driver,
                timeout,
                poll_frequency=self.POLL_FREQUENCY,
            ).until(
                EC.visibility_of_element_located(self.notification_element)
            )
            notification_text = base_page.get_text(self.notification_element)
            self.logger.warning(f"Найдено уведомление: {notification_text}")

            # Проверка на игнорируемые уведомления
            if any(word in notification_text for word in NOTIFICATION_TO_IGNORE):
                self.logger.info(f"Уведомление игнорируется: {notification_text}")
                return notification_text  # Возвращаем текст уведомления, если оно игнорируется

            # Проверка на уведомления, которые прерывают тест
            if any(word in notification_text for word in NOTIFICATION_TO_FAIL):
                self.logger.info(f"Уведомление найдено в списке прерывающих: {notification_text}")
                if ignore_fail_notifications:
                    self.logger.info(f"Уведомление игнорируется: {notification_text}")
                    return notification_text  # Возвращаем текст уведомления
                else:
                    error_message = f"Тест прерван: {notification_text}"
                    if reason:
                        error_message += f" | Дополнительная информация: {reason}"
                    self.logger.error(error_message)
                    pytest.fail(error_message)

            self.logger.info(f"Уведомление не требует действий: {notification_text}")
            return notification_text

        except TimeoutException:
            self.logger.warning("Уведомление не найдено, продолжаем тест.")
            return None
        except Exception as e:
            # A WebDriver/session error is not equivalent to "notification is
            # absent".  Hiding it here produces false-positive tests and makes
            # the next test inherit a broken browser session.
            self.logger.exception("Ошибка при проверке уведомления")
            raise RuntimeError("Не удалось проверить уведомление") from e

    def get_notification_text(self, timeout=10):
        base_page = BasePage(self.driver)
        try:
            WebDriverWait(
                self.driver,
                timeout,
                poll_frequency=self.POLL_FREQUENCY,
            ).until(
                EC.visibility_of_element_located(self.notification_element)
            )
            return base_page.get_text(self.notification_element)
        except TimeoutException:
            message = "Уведомление не найдено в течение {} секунд.".format(timeout)
            self.logger.info(message)
            return message  # Возвращаем сообщение вместо None

    def wait_for_notification_text(self, expected_text, timeout=10):
        """Wait until any visible notification contains ``expected_text``.

        The page can retain several notification containers in the DOM.
        Selenium's standard text condition checks only the first matching
        element, which can be a hidden stale notification while the current
        one is already visible.  Scan every container on each poll instead.
        """
        expected = str(expected_text).strip().casefold()
        if not expected:
            raise ValueError("expected_text must not be empty")

        def visible_matching_text(driver):
            for element in driver.find_elements(*self.notification_element):
                try:
                    text = element.text.strip()
                    if element.is_displayed() and expected in text.casefold():
                        return text
                except Exception:
                    # Notifications are short-lived and may go stale between
                    # discovery and reading; continue scanning current ones.
                    continue
            return False

        text = WebDriverWait(
            self.driver,
            timeout,
            poll_frequency=self.POLL_FREQUENCY,
        ).until(
            visible_matching_text,
            message=(
                f"Видимое уведомление с текстом "
                f"'{expected_text}' не появилось."
            ),
        )
        self.logger.info("Найдено ожидаемое уведомление: %s", text)
        return text

    class CustomErrorFilter():
        def filter(self, record):
            if record.levelname == "ERROR":
                record.levelname = "ERROR__"
            return True
