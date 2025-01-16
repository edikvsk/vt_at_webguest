import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, locator, timeout=20):
        wait = WebDriverWait(self.driver, timeout)
        try:
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            logging.error(f"Элемент не найден: {locator}")
            return None

    def find_element(self, by, value):
        try:
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            logging.error(f"Элемент не найден: {by} = {value}")
            return None

    def find_elements(self, by, value):
        try:
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except TimeoutException:
            logging.error(f"Элементы не найдены: {by} = {value}")
            return []

    def send_keys(self, locator, text):
        element = self.wait_for_element(locator)
        if element:
            element.clear()
            element.send_keys(text)

    def click(self, element_locator, timeout=10):
        """Кликает по элементу, если он доступен, с заданным временем ожидания"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(element_locator)
            )
            element.click()  # Выполняем клик по элементу
        except TimeoutException:
            logging.error(f"Ошибка при клике на элемент: {element_locator}")
            raise RuntimeError(f"Ошибка при клике на элемент: {element_locator}")

    def get_text(self, locator):
        element = self.wait_for_element(locator)
        return element.text if element else ""

    def get_element_value(self, locator):
        element = self.wait_for_element(locator)
        return element.get_attribute("value") if element else ""

    def is_element_present(self, locator, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def is_displayed(self, by, value):
        element = self.find_element(by, value)
        return element.is_displayed() if element else False

    def wait_for_url(self, url, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        try:
            wait.until(EC.url_to_be(url))
        except TimeoutException:
            logging.error(f"URL не соответствует: {url}")

    def is_element_visible(self, locator, timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
