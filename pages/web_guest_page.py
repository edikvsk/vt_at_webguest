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
    VIDEO_BITRATE_COMBOBOX = (By.XPATH, "//div[@class='d-flex flex-grow-1 flex-shrink-1 align-items-center']//span["
                                        "text("")='Video Bitrate']")
    VIDEO_BITRATE_VALUE = (By.XPATH, "//div[@data-cy='videoBitrate']")

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

    def input_text(self, field_locator, text):
        """Вводит указанный текст в заданное поле по одной букве."""
        try:
            text_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(field_locator)
            )
            text_field.clear()
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element_value(field_locator, "")
            )
            for letter in text:
                text_field.send_keys(letter)
                sleep(0.6)
        except Exception as e:
            raise RuntimeError(f"Ошибка при вводе текста: {e}")

    def get_input_value(self, input_locator):
        """Получение значения поля input по указанному локатору."""
        try:
            input_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(input_locator)
            )
            return input_element.get_attribute('value')
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении значения input: {e}")

    def get_volume_fader_value(self, fader_locator):
        """Получение значения aria-valuenow из слайдера по указанному локатору."""
        try:
            # Находим элемент с указанным локатором
            volume_fader = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(fader_locator)
            )

            # Находим внутри него элемент с классом thumb
            thumb_element = volume_fader.find_element(By.XPATH, ".//div[contains(@class, 'thumb')]")

            # Получаем значение aria-valuenow
            return thumb_element.get_attribute('aria-valuenow')
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении значения aria-valuenow: {e}")

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

    def select_from_combobox(self, combobox_locator, text, replacements=None):
        """Выбирает значение из выпадающего списка по заданному тексту."""
        try:
            # Ожидаем, пока комбобокс станет кликабельным и кликаем на него
            combobox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(combobox_locator)
            )
            combobox.click()  # Открываем выпадающий список

            # Если предоставлен словарь замен, выполняем замену текста
            if replacements:
                for original, replacement in replacements.items():
                    if original in text:
                        text = text.replace(original, replacement)
                        break  # Выходим из цикла, если замена выполнена

            # Ожидаем, пока элемент с нужным значением станет видимым
            option_locator = (
                By.XPATH, f"//span[contains(@class, 'menu-item-title') and text()='{text}']"
            )
            option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(option_locator)
            )

            # Ожидаем, пока элемент станет кликабельным и кликаем на него
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(option)
            ).click()

        except Exception as e:
            raise RuntimeError(f"Ошибка при выборе '{text}': {e}")

    def select_resolution(self, resolution_text):
        """Выбирает разрешение из выпадающего списка по заданному тексту."""
        self.select_from_combobox(
            self.RESOLUTION_COMBOBOX,
            resolution_text.replace("X", " × ")
        )

    def select_framerate(self, framerate_text):
        """Выбирает Framerate из выпадающего списка по заданному тексту."""
        self.select_from_combobox(
            self.FRAMERATE_COMBOBOX,
            framerate_text.replace("FPS", "fps")
        )

    def select_audio_bitrate(self, audio_bitrate_text):
        """Выбирает Audio Bitrate из выпадающего списка по заданному тексту."""
        replacements = {
            "AUDIO BITRATE\n6K": "6k",
            "AUDIO BITRATE\n10K": "10k",
            "AUDIO BITRATE\n20K": "20k",
            "AUDIO BITRATE\n40K": "40k",
            "AUDIO BITRATE\n96K": "96k",
            "AUDIO BITRATE\n192K": "192k",
            "AUDIO BITRATE\n510K": "510k"
        }
        self.select_from_combobox(
            self.AUDIO_BITRATE_COMBOBOX,
            audio_bitrate_text,
            replacements
        )

    def select_video_bitrate(self, video_bitrate_text):
        """Выбирает Video Bitrate из выпадающего списка по заданному тексту."""
        replacements = {
            "VIDEO BITRATE\n0.5M": "0.5M",
            "VIDEO BITRATE\n0.75M": "0.75M",
            "VIDEO BITRATE\n1.0M": "1.0M",
            "VIDEO BITRATE\n1.5M": "1.5M",
            "VIDEO BITRATE\n2.5M": "2.5M",
            "VIDEO BITRATE\n5M": "5M",
            "VIDEO BITRATE\n7.5M": "7.5M",
            "VIDEO BITRATE\n10M": "10M",
            "VIDEO BITRATE\n12.5M": "12.5M",
            "VIDEO BITRATE\n15M": "15M",
            "VIDEO BITRATE\n20M": "20M"
        }
        self.select_from_combobox(
            self.VIDEO_BITRATE_COMBOBOX,
            video_bitrate_text,
            replacements
        )
