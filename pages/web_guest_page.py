from time import sleep

from selenium.common import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.base_page import BasePage


class WebGuestPage(BasePage):
    # Локаторы:
    LOGIN_FIELD = (By.XPATH, "//input[@data-cy='banner-name-input']")
    LOCATION_FIELD = (By.XPATH, "//input[@data-cy='banner-location-input']")
    AUTHORIZATION_FORM = (By.XPATH, "//form")
    AUTHORIZATION_NAME_FIELD_ERROR = (
        By.XPATH, "//div[contains(@class, 'error-input')]//span[text()='Please provide name']")
    AUTHORIZATION_LOCATION_FIELD_ERROR = (
        By.XPATH, "//div[contains(@class, 'error-input')]//span[text()='Please provide location']")
    WG_SETTINGS_WINDOW = (By.XPATH, "//div[@data-cy='general-settings']")
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit' and @data-cy='connect-button']")
    SETTINGS_BUTTON = (By.XPATH, "//button[@id='SettingsButtonId']")
    NAME_FIELD_SETTINGS = (By.XPATH, "//input[@data-cy='name-input']")
    LOCATION_FIELD_SETTINGS = (By.XPATH, "//input[@data-cy='location-input']")
    MUTE_BUTTON = (By.XPATH, "//button[@id='PlayButtonId' and @data-cy='mute-remote-button']")
    CAMERA_BUTTON = (By.XPATH, "//button[@id='CameraButtonId']")
    MICROPHONE_BUTTON = (By.XPATH, "//button[@id='MicButtonId']")
    FULLSCREEN_BUTTON = (By.XPATH, "//button[@id='FullscreenButtonId']")
    VOLUME_FADER = (By.XPATH, "//div[@data-cy='sound-settings']")
    MINIMIZE_PREVIEW_BUTTON = (By.XPATH, "//button[contains(@class, 'overflow-minimize-button')]")
    PREVIEW_WINDOW = (By.XPATH, "//video[@data-cy='local-video']")
    CAMERA_TOOLTIP = (By.XPATH, "//div[@id='CameraTooltipId']//span[contains(@class, 'tooltip-title')]")
    MICROPHONE_TOOLTIP = (By.XPATH, "//div[@id='MicTooltipId']//span[contains(@class, 'tooltip-title')]")
    NOTIFICATION_ELEMENT = (By.XPATH, "//div[contains(@class, 'notification-parent')]")
    STOP_BUTTON = (By.XPATH, "//button[.//span[text()='Stop']]")
    START_BUTTON = (By.XPATH, "//button[.//span[text()='Start']]")
    RESOLUTION_COMBOBOX = (By.XPATH, "//span[text()='Resolution']")
    RESOLUTION_VALUE = (By.XPATH, "//div[@data-cy='resolution']//span[contains(@class, 'text-ellipsis')]")
    RESOLUTION_COMBOBOX_BACK_BUTTON = (By.XPATH, "//div[@class='mr-1']")
    FRAMERATE_COMBOBOX = (By.XPATH, "//span[text()='Frame Rate']")
    FRAMERATE_VALUE = (By.XPATH, "//div[@data-cy='frameRate']//span[contains(text(), 'FPS')]")
    AUDIO_BITRATE_COMBOBOX = (By.XPATH, "//span[text()='Audio Bitrate']")
    AUDIO_BITRATE_VALUE = (By.XPATH, "//div[@data-cy='audioBitrate']")
    VIDEO_BITRATE_COMBOBOX = (By.XPATH, "//span[text()='Video Bitrate']")
    VIDEO_BITRATE_VALUE = (By.XPATH, "//div[@data-cy='videoBitrate']")
    VIDEO_ENCODER_COMBOBOX = (By.XPATH, "//span[text()='Video Encoder']")
    VIDEO_ENCODER_VALUE = (By.XPATH, "//div[@data-cy='encoder']//span[contains(@class, 'text-ellipsis')]")
    COMBOBOX_BACK_BUTTON = (By.XPATH, "//div[@class='mr-1']")
    MIRRORING_SWITCHER = (By.XPATH, "//div[@data-cy='mirroring']//div[contains(@class, 'custom-switcher')]")
    AUDIO_ENHANCEMENTS_SWITCHER = (By.XPATH, "//div[@data-cy='audioEnhancements']//div[contains(@class, "
                                             "'custom-switcher')]")
    PREVIEW_MINIMIZE_BUTTON = (By.XPATH, "//button[contains(@class, 'overflow-minimize-button') and @type='button']")
    PREVIEW_CHANGE_BUTTON = (By.XPATH, "//div[@class='d-flex align-items-center justify-content-center flex-shrink-1 "
                                       "flex-grow-1 position-relative']//button")
    PREVIEW_VOLUME_FADER = (By.XPATH, "//span[@class='control-title' and text()='Volume']")
    PREVIEW_REMOTE_WINDOW = (By.XPATH, "//video[@data-cy='remote-video']")
    PREVIEW_MUTE_BUTTON = (By.XPATH, "//div[contains(@class, 'mute-button')]//button[@id='PlayButtonId']")
    INPUT_CAMERA_VALUE = (By.XPATH, "//div[@data-cy='videoInput']//span[contains(@class, 'text-ellipsis')]")
    INPUT_CAMERA_COMBOBOX = (By.XPATH, "//span[text()='Select a camera']")
    INPUT_MICROPHONE_VALUE = (By.XPATH, "//div[@data-cy='audioInput']//span[contains(@class, 'text-ellipsis')]")
    INPUT_MICROPHONE_COMBOBOX = (By.XPATH, "//span[text()='Select a mic']")
    VOLUME_FADER_PREVIEW = (
        By.XPATH, "//div[contains(@class, 'friend-sound-control')]//div[contains(@class, 'react-slider')]")
    AUDIO_CHANNELS_COMBOBOX = (By.XPATH, "//span[text()='Audio Channels']")
    AUDIO_CHANNELS_VALUE = (By.XPATH, "//div[@data-cy='audioChannels']//span[@class='text-uppercase "
                                      "font-weight-semi-bold text-ellipsis text-white']")
    INPUT_FIELD_OTHER_CHANNELS = (By.XPATH, "//div[@class='px-3 pt-4']//input[@class='border-0 outline-none "
                                            "overflow-hidden px-3 text-white input']")
    SCROLLBAR_SELECT_DEVICE = (By.XPATH, "//div[@class='d-flex hidden-scrollbar flex-column overflow-x-hidden']")

    # Методы:
    def click_element_with_scroll(self, element_locator, timeout=10):
        """Кликает по элементу, если он доступен, с заданным временем ожидания и прокруткой к элементу"""
        try:
            # Ожидаем, пока элемент станет кликабельным
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(element_locator)
            )

            # Прокручиваем к элементу, если он не виден
            self.driver.execute_script("arguments[0].scrollIntoView();", element)

            # Используем ActionChains для клика
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()

        except TimeoutException:
            print(f"Элемент {element_locator} не доступен для клика в течение {timeout} секунд.")
        except Exception as e:
            print(f"Ошибка при клике на элемент {element_locator}: {e}")

    def wait_for_element(self, locator, timeout=10):
        """Ожидание элемента по локатору."""
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))

    def hover_element(self, element):
        """Наведение курсора на указанный элемент."""
        ActionChains(self.driver).move_to_element(self.wait_for_element(element)).perform()

    def get_tooltip_text(self, element, tooltip_locator):
        """Получение текста тултипа после наведения на указанный элемент."""
        try:
            self.hover_element(element)
            tooltip_element = self.wait_for_element(tooltip_locator)
            return tooltip_element.text
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Ошибка при получении текста tooltip: {e}")
            return None

    def is_button_pressed(self, button_locator):
        """Проверяет, нажата ли кнопка, используя указанный локатор."""
        try:
            button = self.wait_for_element(button_locator)
            return 'bg-danger' not in button.get_attribute('class')
        except NoSuchElementException as e:
            print(f"Ошибка при проверке состояния кнопки: {e}")
            return False

    def input_text(self, field_locator, text):
        """Вводит указанный текст в заданное поле по одной букве."""
        try:
            text_field = self.wait_for_element(field_locator)
            text_field.clear()
            for letter in text:
                text_field.send_keys(letter)
                sleep(0.5)
        except Exception as e:
            raise RuntimeError(f"Ошибка при вводе текста: {e}")

    def delete_text(self, field_locator):
        """Удаляет текст из заданного поля по одной букве до полного очищения."""
        try:
            text_field = self.wait_for_element(field_locator)
            while text_field.get_attribute('value'):  # Проверяем, есть ли текст в поле
                text_field.send_keys(Keys.BACKSPACE)  # Удаляем последнюю букву
                sleep(0.5)  # Задержка для наглядности
        except Exception as e:
            raise RuntimeError(f"Ошибка при удалении текста: {e}")

    def get_input_value(self, input_locator):
        """Получение значения поля input по указанному локатору."""
        try:
            input_element = self.wait_for_element(input_locator)
            return input_element.get_attribute('value')
        except NoSuchElementException as e:
            raise RuntimeError(f"Ошибка при получении значения input: {e}")

    def get_window_resolution(self):
        """Получение разрешения окна браузера в формате 'width x height'."""
        try:
            window_size = self.driver.get_window_size()
            width = window_size['width']
            height = window_size['height']
            return f"{width} x {height}"
        except WebDriverException as e:
            print(f"Ошибка при получении разрешения окна: {e}")
            return None

    def set_window_resolution(self, width, height):
        """Установка разрешения окна браузера."""
        try:
            self.driver.set_window_size(width, height)
        except WebDriverException as e:
            print(f"Ошибка при установке разрешения окна: {e}")

    def get_volume_fader_value(self, fader_locator):
        """Получение значения aria-valuenow из слайдера по указанному локатору."""
        try:
            volume_fader = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(fader_locator)
            )

            if not volume_fader.is_displayed():
                self.hover_element(self.MUTE_BUTTON)
                volume_fader = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(fader_locator)
                )

            thumb_element = WebDriverWait(volume_fader, 10).until(
                EC.visibility_of_element_located((By.XPATH, ".//div[contains(@class, 'thumb')]"))
            )

            return thumb_element.get_attribute('aria-valuenow')
        except NoSuchElementException as e:
            raise RuntimeError(f"Ошибка при получении значения aria-valuenow: {e}")
        except TimeoutException as e:
            raise RuntimeError(f"Время ожидания истекло: {e}")

    def set_volume_fader_value(self, fader_locator, value):
        """Установка значения слайдера"""
        try:
            volume_fader = self.wait_for_element(fader_locator)
            thumb_element = volume_fader.find_element(By.XPATH, ".//div[contains(@class, 'thumb')]")

            thumb_element.click()

            steps = int(value / 1)
            for _ in range(steps):
                thumb_element.send_keys(Keys.ARROW_RIGHT)

        except NoSuchElementException as e:
            raise RuntimeError(f"Ошибка при установке значения слайдера: {e}")

    def set_volume_fader_value_with_events(self, fader_locator, value):
        """Установка значения слайдера и вызов необходимых событий."""
        try:
            volume_fader = self.wait_for_element(fader_locator)
            thumb_element = volume_fader.find_element(By.XPATH, ".//div[contains(@class, 'thumb')]")

            # Получаем минимальное и максимальное значения
            min_value = int(thumb_element.get_attribute('aria-valuemin'))
            max_value = int(thumb_element.get_attribute('aria-valuemax'))

            # Проверяем, что значение в допустимых пределах
            if value < min_value or value > max_value:
                raise ValueError(f"Значение должно быть в пределах от {min_value} до {max_value}.")

            # Устанавливаем значение с помощью JavaScript
            self.driver.execute_script(f"arguments[0].setAttribute('aria-valuenow', {value});", thumb_element)

            # Вызываем события, если это необходимо
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", thumb_element)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", thumb_element)

        except NoSuchElementException as e:
            raise RuntimeError(f"Ошибка при установке значения слайдера с событиями: {e}")

    def get_settings_item_value_text(self, element_locator):
        """Получение текста элемента по указанному локатору."""
        try:
            element = self.wait_for_element(element_locator)
            return element.text
        except TimeoutException:
            raise RuntimeError(f"Элемент не найден по локатору: {element_locator}")
        except NoSuchElementException as e:
            raise RuntimeError(f"Ошибка при получении текста элемента: {e}")

    def get_options_from_combobox(self, combobox_locator):
        """Возвращает список значений из выпадающего списка."""
        try:
            # Ожидание, пока комбобокс станет кликабельным
            combobox = self.wait_for_element(combobox_locator)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(combobox))

            combobox.click()  # Открываем выпадающий список

            # Ожидание появления всех опций в выпадающем списке
            options_locator = (By.XPATH, "//span[contains(@class, 'menu-item-title')]")
            options = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located(options_locator))

            # Извлекаем текст из всех опций
            options_text = [option.text for option in options if option.is_displayed()]

            return options_text

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return []

    def is_vertical_scrollbar_visible(self, element_locator):
        """
        Проверяет, отображается ли вертикальный скроллбар у элемента.

        :param element_locator: Локатор элемента, для которого проверяется наличие вертикального скроллбара.
        :return: True, если вертикальный скроллбар виден, иначе False.
        """
        try:
            # Ожидание, пока элемент станет видимым
            element = self.wait_for_element(element_locator)
            WebDriverWait(self.driver, 10).until(EC.visibility_of(element))

            # Используем JavaScript для проверки наличия вертикального скроллбара
            script = """
            const element = arguments[0];
            return element.scrollHeight > element.clientHeight;
            """
            has_vertical_scrollbar = self.driver.execute_script(script, element)
            return has_vertical_scrollbar

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return False

    def select_from_combobox(self, combobox_locator, text, replacements=None):
        """Выбирает значение из выпадающего списка по заданному тексту."""
        try:
            combobox = self.wait_for_element(combobox_locator)

            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(combobox))

            combobox.click()

            if replacements:
                for original, replacement in replacements.items():
                    if original in text:
                        text = text.replace(original, replacement)
                        break

            text_lower = text.lower()
            option_locator = (By.XPATH, f"//span[contains(@class, 'menu-item-title')]")

            options = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located(option_locator))

            option_to_select = None
            for option in options:
                if option.is_displayed() and option.text.lower() == text_lower:
                    option_to_select = option
                    break

            if option_to_select and option_to_select.is_enabled():
                option_to_select.click()
            else:
                print("Элемент не доступен для клика или не найден.")

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def select_resolution(self, resolution_text):
        """Выбирает разрешение из выпадающего списка по заданному тексту."""
        self.hover_element(self.RESOLUTION_COMBOBOX)
        self.select_from_combobox(self.RESOLUTION_COMBOBOX, resolution_text.replace("X", " × "))

    def select_framerate(self, framerate_text):
        """Выбирает Framerate из выпадающего списка по заданному тексту."""
        self.hover_element(self.FRAMERATE_COMBOBOX)
        self.select_from_combobox(self.FRAMERATE_COMBOBOX, framerate_text.replace("FPS", "fps"))

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

        self.hover_element(self.AUDIO_BITRATE_COMBOBOX)
        self.select_from_combobox(self.AUDIO_BITRATE_COMBOBOX, audio_bitrate_text, replacements)

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

        self.hover_element(self.VIDEO_BITRATE_COMBOBOX)
        self.select_from_combobox(self.VIDEO_BITRATE_COMBOBOX, video_bitrate_text, replacements)

    def select_video_encoder(self, video_encoder_text):
        """Выбирает Video Encoder из выпадающего списка по заданному тексту."""
        self.hover_element(self.VIDEO_ENCODER_COMBOBOX)
        self.select_from_combobox(self.VIDEO_ENCODER_COMBOBOX, video_encoder_text)

    def select_camera(self, input_camera_text):
        """Выбирает Input Camera из выпадающего списка по заданному тексту."""
        self.hover_element(self.INPUT_CAMERA_COMBOBOX)
        self.select_from_combobox(self.INPUT_CAMERA_COMBOBOX, input_camera_text)

    def select_microphone(self, input_microphone_text):
        """Выбирает Input Mic из выпадающего списка по заданному тексту."""
        self.hover_element(self.INPUT_MICROPHONE_COMBOBOX)
        self.select_from_combobox(self.INPUT_MICROPHONE_COMBOBOX, input_microphone_text)

    def select_audio_channels(self, audio_channels_text):
        """Выбирает Audio Channels из выпадающего списка по заданному тексту."""
        self.hover_element(self.AUDIO_CHANNELS_COMBOBOX)
        self.select_from_combobox(self.AUDIO_CHANNELS_COMBOBOX, audio_channels_text)

    def is_switcher_active(self, switcher_locator):
        """Проверяет, активен ли свитчер, используя указанный локатор."""
        try:
            switcher = self.wait_for_element(switcher_locator)
            return 'bg-success' in switcher.get_attribute('class') and 'bg-danger' not in switcher.get_attribute(
                'class')
        except NoSuchElementException as e:
            print(f"Ошибка при проверке состояния свитчера: {e}")
            return False

    def is_fullscreen(self):
        """Проверяет, находится ли окно в полноэкранном режиме."""
        fullscreen_state = self.driver.execute_script("return document.fullscreenElement !== null;")
        return fullscreen_state

    def is_fullscreen_button_pressed(self, button_locator):
        """Проверяет, нажата ли кнопка FullScreen, используя указанный локатор."""
        try:
            button = self.wait_for_element(button_locator)
            svg_element = button.find_element(By.TAG_NAME, 'svg')
            path_element = svg_element.find_element(By.TAG_NAME, 'path')
            path_data = path_element.get_attribute('d')

            # Проверяем, соответствует ли path_data состоянию 1 (выключено)
            if path_data == "M20 3H22V9H20V5H16V3H20ZM4 3H8V5H4V9H2V3H4ZM20 19V15H22V21H16V19H20ZM4 19H8V21H2V15H4V19Z":
                print("Кнопка в состоянии ВЫКЛ.")
                return True  # Кнопка выключена
            else:
                print("Кнопка в состоянии ВКЛ.")
                return False  # Кнопка включена
        except NoSuchElementException as e:
            print(f"Ошибка при проверке состояния кнопки: {e}")
            return False
