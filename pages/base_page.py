from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        # self.driver.maximize_window()

    def wait_for_element(self, locator, timeout=20):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def send_keys(self, locator, text):
        element = self.wait_for_element(locator)
        element.clear()  # Очистка поля перед вводом текста
        element.send_keys(text)

    def click(self, element_locator):
        """Кликает по элементу, если он доступен"""
        try:
            element = self.wait_for_element(element_locator)  # Ждем, пока элемент станет доступным
            element.click()  # Выполняем клик по элементу
        except TimeoutException:
            print(f"Элемент {element_locator} не доступен для клика.")

    def get_text(self, locator):
        return self.wait_for_element(locator).text

    def get_element_value(self, locator):
        return self.wait_for_element(locator).get_attribute("value")

    def is_element_present(self, locator):
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def wait_for_url(self, url, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.url_to_be(url))
