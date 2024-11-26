from time import sleep

from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.base_page import BasePage


class WebGuestPage(BasePage):
    # Локаторы:
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
    RESOLUTION_COMBOBOX = (By.XPATH, "//span[@class='text-uppercase font-weight-semi-bold menu-item-title text-white' "
                                     "and text()='Resolution']")
    RESOLUTION_VALUE = (By.XPATH, "//div[@data-cy='resolution']//span[contains(@class, 'text-ellipsis')]")
    RESOLUTION_COMBOBOX_BACK_BUTTON = (By.XPATH, "//div[@class='mr-1']")
    FRAMERATE_COMBOBOX = (By.XPATH, "//div[@class='d-flex flex-grow-1 flex-shrink-1 align-items-center']//span[text("
                                    ")='Frame Rate']")
    FRAMERATE_VALUE = (By.XPATH, "//div[@data-cy='frameRate']//span[contains(text(), 'FPS')]")
    COMBOBOX_BACK_BUTTON = (By.XPATH, "//div[@class='mr-1']")
    AUDIO_BITRATE_COMBOBOX = (By.XPATH, "//div[@class='d-flex flex-grow-1 flex-shrink-1 align-items-center']//span["
                                        "text("")='Audio Bitrate']")
    AUDIO_BITRATE_VALUE = (By.XPATH, "//div[@data-cy='audioBitrate']")

    # Методы:
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
            raise RuntimeError(f"Ошибка при вводе имени: {e}")

    def input_location(self, location):
        """Вводит location по одной букве."""
        try:
            location_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.LOCATION_FIELD_SETTINGS)
            )
            location_field.clear()
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element_value(self.LOCATION_FIELD_SETTINGS, "")
            )
            for letter in location:
                location_field.send_keys(letter)
                sleep(0.5)
        except Exception as e:
            raise RuntimeError(f"Ошибка при вводе местоположения: {e}")

    def get_input_value(self, input_locator):
        """Получение значения поля input по указанному локатору."""
        try:
            input_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(input_locator)
            )
            return input_element.get_attribute('value')
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении значения input: {e}")

    def get_settings_item_value_text(self, element_locator):
        """Получение текста элемента по указанному локатору."""
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(element_locator)
            )
            return element.text
        except TimeoutException:
            raise RuntimeError(f"Элемент не найден по локатору: {element_locator}")
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении текста элемента: {e}")

    def select_resolution(self, resolution_text):
        """Выбирает разрешение из выпадающего списка по заданному тексту."""
        try:
            # Ожидаем, пока комбобокс станет кликабельным и кликаем на него
            resolution_combobox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.RESOLUTION_COMBOBOX)
            )
            resolution_combobox.click()  # Открываем выпадающий список

            # Генерируем правильный текст с символом "×"
            resolution_text = resolution_text.replace("X", " × ")

            # Ожидаем, пока элемент с нужным разрешением станет видимым
            resolution_option_locator = (
                By.XPATH, f"//span[contains(@class, 'menu-item-title') and text()='{resolution_text}']")

            resolution_option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(resolution_option_locator)
            )

            # Ожидаем, пока элемент станет кликабельным и кликаем на него
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(resolution_option)
            ).click()

        except Exception as e:
            raise RuntimeError(f"Ошибка при выборе разрешения '{resolution_text}': {e}")

    def select_framerate(self, framerate_text):
        """Выбирает Framerate из выпадающего списка по заданному тексту."""
        try:
            # Ожидаем, пока комбобокс станет кликабельным и кликаем на него
            framerate_combobox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.FRAMERATE_COMBOBOX)
            )
            framerate_combobox.click()  # Открываем выпадающий список

            # Генерируем правильный текст с символом
            framerate_text = framerate_text.replace("FPS", "fps")

            # Ожидаем, пока элемент с нужным Framerate станет видимым
            framerate_option_locator = (
                By.XPATH, f"//span[contains(@class, 'menu-item-title') and text()='{framerate_text}']")

            framerate_option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(framerate_option_locator)
            )

            # Ожидаем, пока элемент станет кликабельным и кликаем на него
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(framerate_option)
            ).click()

        except Exception as e:
            raise RuntimeError(f"Ошибка при выборе Framerate '{framerate_text}': {e}")

    def select_audio_bitrate(self, audio_bitrate_text):
        """Выбирает Audio Bitrate из выпадающего списка по заданному тексту."""
        try:
            # Ожидаем, пока комбобокс станет кликабельным и кликаем на него
            audio_bitrate_combobox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.AUDIO_BITRATE_COMBOBOX)
            )
            audio_bitrate_combobox.click()  # Открываем выпадающий список

            # Словарь для замены значений
            replacements = {
                "AUDIO BITRATE\n6K": "6k",
                "AUDIO BITRATE\n10K": "10k",
                "AUDIO BITRATE\n20K": "20k",
                "AUDIO BITRATE\n40K": "40k",
                "AUDIO BITRATE\n96K": "96k",
                "AUDIO BITRATE\n192K": "192k",
                "AUDIO BITRATE\n510K": "510k"
            }

            # Заменяем значения в соответствии со словарем
            for original, replacement in replacements.items():
                if original in audio_bitrate_text:
                    audio_bitrate_text = audio_bitrate_text.replace(original, replacement)
                    break  # Выходим из цикла, если замена выполнена

            # Ожидаем, пока элемент с нужным Audio Bitrate станет видимым
            audio_bitrate_option_locator = (
                By.XPATH, f"//span[contains(@class, 'menu-item-title') and text()='{audio_bitrate_text}']"
            )

            audio_bitrate_option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(audio_bitrate_option_locator)
            )

            # Ожидаем, пока элемент станет кликабельным и кликаем на него
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(audio_bitrate_option)
            ).click()

        except Exception as e:
            raise RuntimeError(f"Ошибка при выборе Audio Bitrate '{audio_bitrate_text}': {e}")


