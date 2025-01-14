from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
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

    def click(self, element_locator, timeout=10):
        """Кликает по элементу, если он доступен, с заданным временем ожидания"""
        try:
            # Ожидаем, пока элемент станет кликабельным
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(element_locator)
            )
            element.click()  # Выполняем клик по элементу
        except TimeoutException:
            raise RuntimeError(f"Ошибка при клике на элемент: {element_locator}")

    def get_text(self, locator):
        return self.wait_for_element(locator).text

    def get_element_value(self, locator):
        return self.wait_for_element(locator).get_attribute("value")

    def is_element_present(self, locator, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def wait_for_url(self, url, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.url_to_be(url))

    def is_element_visible(self, locator, timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def select_from_combobox(self, combobox_locator, text, replacements=None):
        """Выбирает значение из выпадающего списка по заданному тексту."""
        try:
            combobox = self.wait_for_element(combobox_locator)

            # Ожидание, пока элемент станет кликабельным
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(combobox))

            combobox.click()  # Открываем выпадающий список

            # Если предоставлен словарь замен, выполняем замену текста
            if replacements:
                for original, replacement in replacements.items():
                    if original in text:
                        text = text.replace(original, replacement)
                        break  # Выходим из цикла, если замена выполнена

            option_locator = (By.XPATH, f"//span[contains(@class, 'menu-item-title') and text()='{text}']")

            # Ожидание, пока элемент станет кликабельным
            option = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(option_locator))

            # Проверка, что элемент видим и доступен для клика
            if option.is_displayed() and option.is_enabled():
                option.click()
            else:
                print("Элемент не доступен для клика.")

        except Exception as e:
            print(f"Произошла ошибка: {e}")
