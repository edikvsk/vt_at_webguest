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
    MUTE_BUTTON = (By.XPATH, "//button[@id='PlayButtonId']")
    CAMERA_BUTTON = (By.XPATH, "//button[@id='CameraButtonId']")
    MICROPHONE_BUTTON = (By.XPATH, "//button[@id='MicButtonId']")
    FULLSCREEN_BUTTON = (By.XPATH, "//button[@id='FullscreenButtonId']")
    STOP_BUTTON = (By.XPATH, "//button[.//span[text()='Stop']]")
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
            # Ожидаем появления кнопки
            button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(button_locator)
            )

            # Проверяем, содержит ли кнопка класс, указывающий на активное состояние
            return 'bg-danger' not in button.get_attribute('class')
        except Exception as e:
            print(f"Ошибка при проверке состояния кнопки: {e}")
            return False
