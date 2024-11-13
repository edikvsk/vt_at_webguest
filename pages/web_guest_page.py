import random
from time import sleep

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.base_page import BasePage


class WebGuestPage(BasePage):
    LOGIN_FIELD = (By.XPATH, "//input[@data-cy='banner-name-input']")
    LOCATION_FIELD = (By.XPATH, "//input[@data-cy='banner-location-input']")
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit' and @data-cy='connect-button']")
    SETTINGS_BUTTON = (By.XPATH, "//button[@id='SettingsButtonId']")
    NAME_FIELD_SETTINGS = (By.XPATH, "//input[@data-cy='name-input']")
    LOCATION_FIELD_SETTINGS = (By.XPATH, "//input[@data-cy='location-input']")
    MUTE_BUTTON = (By.XPATH, "//button[@id='PlayButtonId' and @data-cy='mute-remote-button']")
    CAMERA_BUTTON = (By.XPATH, "//button[@id='CameraButtonId']")
    MICROPHONE_BUTTON = (By.XPATH, "//button[@id='MicButtonId']")
    FULLSCREEN_BUTTON = (By.XPATH, "//button[@id='FullscreenButtonId']")
    VOLUME_FADER = (By.XPATH, "//div[@data-cy='sound-settings']")
    MINIMIZE_PREVIEW_BUTTON = (By.XPATH, "//button[@class='d-flex border-0 outline-none base-button "
                                         "align-items-center justify-content-center custom-button p-0 icon-button "
                                         "active position-absolute overflow-minimize-button default-button']")
    PREVIEW_WINDOW = (By.XPATH, "//div[@class='d-flex align-items-center justify-content-center flex-shrink-1 "
                                "flex-grow-1 position-relative']")
    CAMERA_TOOLTIP = (By.XPATH, "//div[@id='CameraTooltipId']//span[@class='text-uppercase tooltip-title']")
    MICROPHONE_TOOLTIP = (By.XPATH, "//div[@id='MicTooltipId']//span[@class='text-uppercase tooltip-title']")
    NOTIFICATION_ELEMENT = (By.XPATH, "//div[@class='notification-container-top-right']//div[contains(@class, "
                                      "'notification-parent')]")
    STOP_BUTTON = (By.XPATH, "//button[.//span[text()='Stop']]")
    START_BUTTON = (By.XPATH, "//button[.//span[text()='Start']]")

    def get_username(self):
        return self.get_text(self.LOGIN_FIELD)

    def hover_element(self, element):
        """Наведение курсора на указанный элемент."""
        element_to_hover = self.wait_for_element(element)
        ActionChains(self.driver).move_to_element(element_to_hover).perform()

    def get_tooltip_text(self, element, tooltip_locator):
        """Получение текста тултипа после наведения на указанный элемент."""
        try:
            self.hover_element(element)
            tooltip_element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(tooltip_locator)
            )
            return tooltip_element.text
        except Exception as e:
            print(f"Ошибка при получении текста tooltip: {e}")
            return None

    def is_button_pressed(self, button_locator):
        """Проверяет, нажата ли кнопка, используя указанный локатор."""
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(button_locator)
            )
            return 'bg-danger' not in button.get_attribute('class')
        except Exception as e:
            print(f"Ошибка при проверке состояния кнопки: {e}")
            return False

    def input_name(self, name):
        """Вводит указанное имя в поле имени по одной букве."""
        try:
            name_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.NAME_FIELD_SETTINGS)
            )
            name_field.clear()
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element_value(self.NAME_FIELD_SETTINGS, "")
            )
            for letter in name:
                name_field.send_keys(letter)
                sleep(0.7)

        except Exception as e:
            print(f"Ошибка при вводе имени: {e}")

    def generate_random_name(self):
        """Генерирует случайное имя в формате 'NameXXXX', где XXXX - случайное число."""
        random_value = random.randint(1000, 9999)
        return f"Name{random_value}"

    def input_location(self, location):
        """Вводит указанное местоположение в поле локации."""
        try:
            location_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.LOCATION_FIELD_SETTINGS)
            )
            location_field.clear()
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element_value(self.LOCATION_FIELD_SETTINGS, "")
            )
            location_field.send_keys(location)
        except Exception as e:
            print(f"Ошибка при вводе локации: {e}")

    def get_input_value(self, input_locator):
        """Получение значения поля input по указанному локатору."""
        try:
            input_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(input_locator)
            )
            return input_element.get_attribute('value')
        except Exception as e:
            print(f"Ошибка при получении значения input: {e}")
            return None

    def get_name_field_value(self):
        """Получение значения поля имени."""
        return self.get_input_value(self.NAME_FIELD_SETTINGS)

    def get_location_field_value(self):
        """Получение значения поля Location."""
        return self.get_input_value(self.LOCATION_FIELD_SETTINGS)
