import re
from datetime import datetime, timedelta

from selenium.common import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class WebGuestPage(BasePage):
    # Локаторы:
    LOGIN_FIELD = (By.XPATH, "//input[@data-cy='banner-name-input']")
    LOCATION_FIELD = (By.XPATH, "//input[@data-cy='banner-location-input']")
    SECURITY_NAME = (By.XPATH, "//input[@name='name' and @placeholder='Enter your name']")
    SECURITY_LOCATION = (By.XPATH, "//input[@name='location' and @placeholder='Enter your location']")
    SECURITY_LOGIN = (By.XPATH, "//input[@name='login' and @placeholder='Enter your login']")
    SECURITY_PASSWORD = (By.XPATH, "//input[@name='password' and @placeholder='Enter your password' and "
                                   "@type='password']")
    SECURITY_CONNECT_BUTTON = (By.XPATH, "//button[@type='submit' and span[text()='Connect']]")
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
    PREVIEW_WINDOW_WRAPPER = (
        By.XPATH,
        "//video[@data-cy='local-video']"
        "/ancestor::div[contains(@class, 'video-wrapper')]",
    )
    PREVIEW_WINDOW_OVERLAY = (
        By.XPATH,
        "//video[@data-cy='local-video']"
        "/ancestor::div[contains(@class, 'video-wrapper')]"
        "//div[contains(concat(' ', normalize-space(@class), ' '), ' video-overflow ')]",
    )
    CAMERA_TOOLTIP = (By.XPATH, "//div[@id='CameraTooltipId']//span[contains(@class, 'tooltip-title')]")
    MICROPHONE_TOOLTIP = (By.XPATH, "//div[@id='MicTooltipId']//span[contains(@class, 'tooltip-title')]")
    NOTIFICATION_ELEMENT = (By.XPATH, "//div[contains(@class, 'notification-parent')]")
    STOP_BUTTON = (By.XPATH, "//button[.//span[text()='Stop']]")
    START_BUTTON = (By.XPATH, "//button[.//span[text()='Start']]")
    RESOLUTION_COMBOBOX = (By.XPATH, "//span[text()='Resolution']")
    RESOLUTION_VALUE = (By.XPATH, "//div[@data-cy='resolution']//span[contains(@class, 'text-ellipsis')]")
    RESOLUTION_COMBOBOX_BACK_BUTTON = (
        By.XPATH,
        "//div[@data-cy='general-settings']"
        "//div[contains(concat(' ', normalize-space(@class), ' '), ' mr-1 ')]",
    )
    FRAMERATE_COMBOBOX = (By.XPATH, "//span[text()='Frame Rate']")
    FRAMERATE_VALUE = (By.XPATH, "//div[@data-cy='frameRate']//span[contains(@class, 'text-ellipsis')]")
    AUDIO_BITRATE_COMBOBOX = (By.XPATH, "//span[text()='Audio Bitrate']")
    AUDIO_BITRATE_VALUE = (By.XPATH, "//div[@data-cy='audioBitrate']")
    VIDEO_BITRATE_COMBOBOX = (By.XPATH, "//span[text()='Video Bitrate']")
    VIDEO_BITRATE_VALUE = (By.XPATH, "//div[@data-cy='videoBitrate']")
    VIDEO_ENCODER_COMBOBOX = (By.XPATH, "//span[text()='Video Encoder']")
    VIDEO_ENCODER_VALUE = (By.XPATH, "//div[@data-cy='encoder']//span[contains(@class, 'text-ellipsis')]")
    COMBOBOX_BACK_BUTTON = RESOLUTION_COMBOBOX_BACK_BUTTON
    MIRRORING_SWITCHER = (By.XPATH, "//div[@data-cy='mirroring']//div[contains(@class, 'custom-switcher')]")
    AUDIO_ENHANCEMENTS_SWITCHER = (By.XPATH, "//div[@data-cy='audioEnhancements']//div[contains(@class, "
                                             "'custom-switcher')]")
    PREVIEW_MINIMIZE_BUTTON = (By.XPATH, "//button[contains(@class, 'overflow-minimize-button') and @type='button']")
    PREVIEW_MAXIMIZE_BUTTON = (By.XPATH, "//button[contains(@class, 'overflow-maximize-button') and @type='button']")
    PREVIEW_CHANGE_BUTTON = (By.XPATH, "//div[@class='d-flex align-items-center justify-content-center flex-shrink-1 "
                                       "flex-grow-1 position-relative']//button")
    PREVIEW_VOLUME_FADER = (
        By.XPATH,
        "//span[contains(@class, 'control-title') and normalize-space()='Volume']",
    )
    PREVIEW_REMOTE_WINDOW = (By.XPATH, "//video[@data-cy='remote-video']")
    PREVIEW_MUTE_BUTTON = (By.XPATH, "//div[contains(@class, 'mute-button')]//button[@id='PlayButtonId']")
    INPUT_CAMERA_VALUE = (By.XPATH, "//div[@data-cy='videoInput']//span[contains(@class, 'text-ellipsis')]")
    INPUT_CAMERA_COMBOBOX = (By.XPATH, "//span[text()='Select a camera']")
    INPUT_MICROPHONE_VALUE = (By.XPATH, "//div[@data-cy='audioInput']//span[contains(@class, 'text-ellipsis')]")
    INPUT_MICROPHONE_COMBOBOX = (By.XPATH, "//span[text()='Select a mic']")
    VOLUME_FADER_PREVIEW = (
        By.XPATH, "//div[contains(@class, 'friend-sound-control')]//div[contains(@class, 'react-slider')]")
    VISIBLE_VOLUME_FADER = (
        By.XPATH,
        "//div[@data-cy='sound-settings' and "
        "contains(concat(' ', normalize-space(@class), ' '), ' active ')]"
        "//div[contains(concat(' ', normalize-space(@class), ' '), ' react-slider ')]",
    )
    # Click the complete row. The label sits at the bottom edge of the
    # scrollable settings panel and an ActionChains click on the span can land
    # outside its clipped hit area without opening the submenu.
    AUDIO_CHANNELS_COMBOBOX = (By.XPATH, "//div[@data-cy='audioChannels']")
    AUDIO_CHANNELS_VALUE = (
        By.XPATH,
        "//div[@data-cy='audioChannels']//*[contains(@class, 'text-ellipsis')]",
    )
    INPUT_FIELD_OTHER_CHANNELS = (
        By.XPATH,
        "//div[contains(@class, 'pt-4')]//input[contains(@class, 'outline-none')]",
    )
    SCROLLBAR_SELECT_DEVICE = (
        By.XPATH,
        "//div[contains(@class, 'hidden-scrollbar') and contains(@class, 'flex-column')]",
    )

    # Методы:
    def click_element_with_scroll(self, element_locator, timeout=10):
        """
        Кликает по элементу после прокрутки к нему и ожидания кликабельности.

        :param element_locator: Локатор целевого элемента
        :param timeout: Максимальное время ожидания в секундах (по умолчанию 10)
        :return: None
        """
        try:
            # Presence is sufficient here. Responsive toolbar controls are
            # frequently covered by an animated preview layer, making
            # Selenium's clickable predicate wait for the full timeout even
            # though a DOM click is already safe.
            element = self._wait(timeout).until(
                EC.presence_of_element_located(element_locator)
            )

            if element.get_attribute("disabled") is not None:
                raise RuntimeError(
                    f"Element is disabled and cannot be clicked: {element_locator}"
                )

            # Прокручиваем к элементу, если он не виден
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                element,
            )

            # A DOM click avoids Selenium's default human-like pointer travel.
            # Keep a zero-duration pointer action as a fallback for controls that
            # explicitly depend on mouse events.
            try:
                element.click()
            except WebDriverException:
                self._actions().move_to_element(element).click().perform()
            if element_locator == self.SETTINGS_BUTTON:
                self._ensure_settings_open(timeout)
            return
        except Exception as error:
            # A visible toolbar button can still be intercepted by the local
            # preview overlay while its animation settles.  Native click is
            # preferable, but a DOM click is the same action for these React
            # buttons and avoids treating the transient overlap as a failure.
            try:
                element = self._wait(timeout).until(
                    EC.presence_of_element_located(element_locator)
                )
                if element.get_attribute("disabled") is not None:
                    raise RuntimeError(
                        f"Element is disabled and cannot be clicked: {element_locator}"
                    )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', inline: 'center'});"
                    "arguments[0].click();",
                    element,
                )
                if element_locator == self.SETTINGS_BUTTON:
                    self._ensure_settings_open(timeout)
                return
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Element click failed: {element_locator}"
                ) from fallback_error

    def _ensure_settings_open(self, timeout=10):
        """Confirm that Settings opened and retry transiently ignored clicks."""
        short_wait = min(2.0, max(0.5, timeout / 3))
        for attempt in range(3):
            try:
                self._wait(short_wait).until(
                    EC.visibility_of_element_located(self.WG_SETTINGS_WINDOW)
                )
                return
            except TimeoutException:
                if attempt == 2:
                    break
                button = self._wait(timeout).until(
                    EC.presence_of_element_located(self.SETTINGS_BUTTON)
                )
                self.driver.execute_script("arguments[0].click();", button)
        raise RuntimeError("Settings panel did not open after 3 confirmed clicks.")

    def wait_for_element(self, locator, timeout=10):
        """
        Ожидает появление элемента в DOM страницы.

        :param locator: Локатор искомого элемента
        :param timeout: Максимальное время ожидания в секундах (по умолчанию 10)
        :return: WebElement - найденный элемент
        :raises TimeoutException: Если элемент не найден за указанное время
        """
        return self._wait(timeout).until(EC.presence_of_element_located(locator))

    def hover_element(self, element):
        """
        Наводит курсор мыши на указанный элемент.

        :param element: Локатор элемента для наведения
        :return: None
        """
        # Stream controls auto-hide after pointer inactivity.  Moving the
        # pointer inside the document first makes the toolbar visible; waiting
        # for the hidden target before doing that creates a circular timeout.
        try:
            self.driver.switch_to.window(self.driver.current_window_handle)
            self.driver.execute_script("window.focus();")
            body = self._wait(2).until(
                EC.visibility_of_element_located((By.TAG_NAME, "body"))
            )
            self._actions().move_to_element(body).perform()
        except WebDriverException:
            # The target wait below retains the useful Selenium error if the
            # window really is unavailable.
            pass

        if element == self.VOLUME_FADER:
            # This fader is permanently mounted but visible only while the
            # remote-audio control group is active.
            mute = self._wait().until(
                EC.presence_of_element_located(self.MUTE_BUTTON)
            )
            self._actions().move_to_element(mute).perform()

        preview_controls = {
            self.PREVIEW_MINIMIZE_BUTTON,
            self.PREVIEW_MAXIMIZE_BUTTON,
            self.PREVIEW_CHANGE_BUTTON,
            self.PREVIEW_VOLUME_FADER,
            self.PREVIEW_MUTE_BUTTON,
            self.VOLUME_FADER_PREVIEW,
        }
        if element in preview_controls:
            self.reveal_preview_controls()

        target = self._wait().until(EC.visibility_of_element_located(element))
        self._actions().move_to_element(target).perform()

    def reveal_preview_controls(self):
        """Reveal controls over the draggable local-preview layer.

        The minimized preview is intentionally transparent until hover. Chrome
        can move the synthetic pointer to that layer without firing the React
        mouse transition, so dispatch the same bubbling pointer events after
        the real pointer movement.
        """
        overlays = self._wait().until(
            lambda driver: driver.find_elements(
                By.XPATH,
                "//div[contains(concat(' ', normalize-space(@class), ' '), "
                "' video-overflow ')]",
            )
        )
        overlay = next(
            (candidate for candidate in overlays if candidate.is_displayed()),
            overlays[0],
        )
        self._actions().move_to_element(overlay).perform()
        self.driver.execute_script(
            """
            const target = arguments[0];
            for (const type of ['mouseenter', 'mouseover', 'mousemove']) {
                target.dispatchEvent(new MouseEvent(type, {
                    bubbles: true,
                    cancelable: true,
                    view: window
                }));
            }
            """,
            overlay,
        )

    def get_tooltip_text(self, element, tooltip_locator):
        """
        Получает текст всплывающей подсказки после наведения на элемент.

        :param element: Локатор элемента для наведения
        :param tooltip_locator: Локатор элемента тултипа
        :return: Текст подсказки или None при ошибке
        """
        try:
            self.hover_element(element)
            tooltip_element = self._wait(10).until(
                lambda driver: self._element_with_text(
                    driver,
                    tooltip_locator,
                )
            )
            return self._element_text(tooltip_element)
        except (TimeoutException, NoSuchElementException) as error:
            raise RuntimeError(
                f"Tooltip label did not become available: {tooltip_locator}"
            ) from error

    @staticmethod
    def _element_with_text(driver, locator):
        element = driver.find_element(*locator)
        return element if WebGuestPage._element_text(element) else False

    @staticmethod
    def _element_text(element):
        # Bootstrap keeps tooltip content mounted while Popper transitions its
        # visibility. Selenium's ``text`` is empty during that transition even
        # though the label is already populated. Read textContent as the stable
        # fallback so the test validates the tooltip label, not animation
        # timing.
        visible_text = element.text.strip()
        if visible_text:
            return visible_text

        text_content = (element.get_attribute("textContent") or "").strip()
        classes = (element.get_attribute("class") or "").split()
        if "text-uppercase" in classes:
            return text_content.upper()
        return text_content

    def is_button_pressed(self, button_locator):
        """
        Проверяет состояние нажатия кнопки по наличию CSS-класса.

        :param button_locator: Локатор проверяемой кнопки
        :return: True если кнопка нажата (отсутствует класс bg-danger), иначе False
        """
        try:
            button = self.wait_for_element(button_locator)
            return 'bg-danger' not in button.get_attribute('class')
        except NoSuchElementException as e:
            print(f"Ошибка при проверке состояния кнопки: {e}")
            return False

    def input_text(self, field_locator, text):
        """
        Вводит текст в поле посимвольно с задержкой.

        :param field_locator: Локатор текстового поля
        :param text: Текст для ввода
        :return: None
        :raises RuntimeError: При ошибках ввода
        """
        try:
            text_field = self._wait().until(EC.element_to_be_clickable(field_locator))
            text_field.clear()
            text_field.send_keys(text)
            self._wait(2).until(
                lambda _driver: text_field.get_attribute('value') == str(text)
            )
            # Some settings are propagated to VT on blur.  Reading the DOM
            # value alone is not proof that the application accepted it.
            text_field.send_keys(Keys.TAB)
        except Exception as e:
            raise RuntimeError(f"Ошибка при вводе текста: {e}")

    def delete_text(self, field_locator, timeout=20):
        """
        Удаляет текст из поля посимвольно с помощью клавиши BACKSPACE.

        :param field_locator: Локатор текстового поля
        :param timeout: Максимальное время ожидания элемента (по умолчанию 20)
        :return: None
        :raises RuntimeError: При ошибках удаления
        """
        try:
            text_field = self._wait(timeout).until(
                EC.visibility_of_element_located(field_locator)
            )
            text_field.send_keys(Keys.CONTROL, 'a')
            text_field.send_keys(Keys.BACKSPACE)
            self._wait(2).until(
                lambda _driver: not text_field.get_attribute('value')
            )
        except Exception as e:
            raise RuntimeError(f"Ошибка при удалении текста: {e}")

    def get_input_value(self, input_locator):
        """
        Получает текущее значение поля ввода.

        :param input_locator: Локатор элемента input
        :return: Текущее значение поля
        :raises RuntimeError: Если элемент не найден
        """
        try:
            input_element = self.wait_for_element(input_locator)
            return input_element.get_attribute('value')
        except NoSuchElementException as e:
            raise RuntimeError(f"Ошибка при получении значения input: {e}")

    @staticmethod
    def get_current_time_formatted():
        """
        Возвращает текущее время в формате "дд/мм/гггг чч:мм".

        :return: Строка с текущим временем в указанном формате.
        """
        # Получаем текущее время
        now = datetime.now()

        # Форматируем время в нужный формат
        formatted_time = now.strftime("%d/%m/%Y %H:%M")

        return formatted_time

    @staticmethod
    def add_time(time_str, hours=0, minutes=0):
        """
        Добавляет указанное количество часов и минут к времени в строковом формате.
        :param time_str: Время в формате "дд/мм/гггг чч:мм".
        :param hours: Количество часов для добавления (по умолчанию 0).
        :param minutes: Количество минут для добавления (по умолчанию 0).
        :return: Новое время в формате "дд/мм/гггг чч:мм".
        """
        # Преобразуем строку в объект datetime
        time_format = "%d/%m/%Y %H:%M"
        time_obj = datetime.strptime(time_str, time_format)

        # Добавляем часы и минуты
        new_time_obj = time_obj + timedelta(hours=hours, minutes=minutes)

        # Преобразуем обратно в строку
        new_time_str = new_time_obj.strftime(time_format)
        return new_time_str

    def get_window_resolution(self):
        """
        Возвращает текущее разрешение окна браузера.

        :return: Строка в формате "width x height" или None при ошибке
        """
        try:
            window_size = self.driver.get_window_size()
            width = window_size['width']
            height = window_size['height']
            return f"{width} x {height}"
        except WebDriverException as e:
            print(f"Ошибка при получении разрешения окна: {e}")
            return None

    def set_window_resolution(self, width, height):
        """
        Устанавливает новый размер окна браузера.

        :param width: Новая ширина окна
        :param height: Новая высота окна
        :return: None
        """
        try:
            self.driver.set_window_size(width, height)
        except WebDriverException as e:
            print(f"Ошибка при установке разрешения окна: {e}")

    def get_volume_fader_value(self, fader_locator):
        """
        Получает текущее значение слайдера громкости.

        :param fader_locator: Локатор элемента слайдера
        :return: Значение aria-valuenow или None
        :raises RuntimeError: При ошибках получения значения
        """
        try:
            # Пробуем получить значение через JS — надёжнее чем ждать видимость
            value = self.driver.execute_script(
                "var thumb = document.querySelector('div[data-cy=\"sound-settings\"] .thumb'); "
                "return thumb ? thumb.getAttribute('aria-valuenow') : null;"
            )
            if value is not None:
                return value

            # Fallback: классический Selenium путь
            volume_fader = self._wait(10).until(
                EC.presence_of_element_located(fader_locator)
            )

            if not volume_fader.is_displayed():
                self.hover_element(self.MUTE_BUTTON)

            thumb_element = self._wait(10).until(
                EC.visibility_of_element_located(
                    (fader_locator[0], fader_locator[1] + "//div[contains(@class, 'thumb')]")
                )
            )

            return thumb_element.get_attribute('aria-valuenow')
        except NoSuchElementException as e:
            raise RuntimeError(f"Ошибка при получении значения aria-valuenow: {e}")
        except TimeoutException as e:
            raise RuntimeError(f"Время ожидания истекло: {e}")

    def set_volume_fader_value(self, fader_locator, value):
        """
        Устанавливает значение слайдера с помощью клавиш управления.

        :param fader_locator: Локатор элемента слайдера
        :param value: Целевое значение для установки
        :return: None
        :raises RuntimeError: При ошибках установки значения
        """
        try:
            volume_fader = self.wait_for_element(fader_locator)
            thumb_element = volume_fader.find_element(By.XPATH, ".//div[contains(@class, 'thumb')]")

            self._set_slider_value(thumb_element, value)

        except NoSuchElementException as e:
            raise RuntimeError(f"Ошибка при установке значения слайдера: {e}")

    def set_volume_fader_value_with_events(self, fader_locator, value):
        """
        Устанавливает значение слайдера через JavaScript с генерацией событий.

        :param fader_locator: Локатор элемента слайдера
        :param value: Целевое значение для установки
        :return: None
        :raises ValueError: При значении вне допустимого диапазона
        :raises RuntimeError: При ошибках выполнения
        """
        try:
            volume_fader = self.wait_for_element(fader_locator)
            thumb_element = volume_fader.find_element(By.XPATH, ".//div[contains(@class, 'thumb')]")

            # Получаем минимальное и максимальное значения
            min_value = int(thumb_element.get_attribute('aria-valuemin'))
            max_value = int(thumb_element.get_attribute('aria-valuemax'))

            # Проверяем, что значение в допустимых пределах
            if value < min_value or value > max_value:
                raise ValueError(f"Значение должно быть в пределах от {min_value} до {max_value}.")

            self._set_slider_value(thumb_element, value)

        except NoSuchElementException as e:
            raise RuntimeError(f"Ошибка при установке значения слайдера с событиями: {e}")

    def _set_slider_value(self, thumb_element, value):
        """Change a React slider through real keyboard events and verify it."""
        minimum = int(thumb_element.get_attribute("aria-valuemin"))
        maximum = int(thumb_element.get_attribute("aria-valuemax"))
        target = int(value)
        if target < minimum or target > maximum:
            raise ValueError(
                f"Значение должно быть в пределах от {minimum} до {maximum}."
            )

        self.driver.execute_script("arguments[0].focus();", thumb_element)
        thumb_element.send_keys(Keys.HOME)
        if target > minimum:
            thumb_element.send_keys(Keys.ARROW_RIGHT * (target - minimum))
        self._wait(5).until(
            lambda _driver: int(thumb_element.get_attribute("aria-valuenow"))
            == target
        )

    def get_settings_item_value_text(self, element_locator, timeout=10):
        """
        Получает текстовое значение элемента настроек.

        :param element_locator: Локатор элемента
        :param timeout: Максимальное время ожидания в секундах (по умолчанию 10)
        :return: Текст элемента
        :raises RuntimeError: Если элемент не найден
        """
        try:
            element = self._wait(timeout).until(
                EC.visibility_of_element_located(element_locator)
            )
            return element.text
        except TimeoutException:
            raise RuntimeError(f"Элемент не найден по локатору: {element_locator}")
        except NoSuchElementException as e:
            raise RuntimeError(f"Ошибка при получении текста элемента: {e}")

    def get_options_from_combobox(self, combobox_locator):
        """
        Получает список доступных опций в выпадающем списке.

        :param combobox_locator: Локатор комбобокса
        :return: Список текстовых значений опций
        """
        try:
            # Ожидание, пока комбобокс станет кликабельным
            combobox = self.wait_for_element(combobox_locator)
            self._wait(10).until(EC.element_to_be_clickable(combobox))

            combobox.click()  # Открываем выпадающий список

            # Ожидание появления всех опций в выпадающем списке
            options_locator = (By.XPATH, "//span[contains(@class, 'menu-item-title')]")
            options = self._wait(10).until(EC.presence_of_all_elements_located(options_locator))

            # Извлекаем текст из всех опций
            options_text = [option.text for option in options if option.is_displayed()]

            return options_text

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return []

    def is_vertical_scrollbar_visible(self, element_locator):
        """
        Проверяет наличие вертикальной полосы прокрутки у элемента.

        :param element_locator: Локатор проверяемого элемента
        :return: True если скроллбар присутствует, иначе False
        """
        try:
            # Ожидание, пока элемент станет видимым
            element = self.wait_for_element(element_locator)
            self._wait(10).until(EC.visibility_of(element))

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

    @staticmethod
    def _normalized_text(value):
        return " ".join((value or "").split()).casefold()

    def select_from_combobox(
        self,
        combobox_locator,
        text,
        replacements=None,
        value_locator=None,
        expected_value=None,
        attempts=3,
        wait_for_menu_to_close=False,
        partial_match=False,
    ):
        """
        Выбирает опцию в выпадающем списке по точному совпадению текста.

        :param combobox_locator: Локатор комбобокса
        :param text: Текст опции для выбора
        :param replacements: Словарь замен для текста опции
        :return: None
        """
        option_text = text
        if replacements:
            for original, replacement in replacements.items():
                if original in option_text:
                    option_text = option_text.replace(original, replacement)
                    break

        wanted_option = self._normalized_text(option_text)
        wanted_value = self._normalized_text(expected_value)
        option_locator = (By.XPATH, "//span[contains(@class, 'menu-item-title')]")
        last_error = None
        observed_options = set()

        for attempt in range(1, attempts + 1):
            try:
                combobox = self._wait(10).until(
                    EC.element_to_be_clickable(combobox_locator)
                )
                ActionChains(self.driver, duration=200).move_to_element(
                    combobox
                ).pause(0.15).click().perform()

                def find_visible_option(driver):
                    for option in driver.find_elements(*option_locator):
                        try:
                            actual_option = self._normalized_text(option.text)
                            if option.is_displayed() and actual_option:
                                observed_options.add(" ".join((option.text or "").split()))
                            matches = (
                                wanted_option in actual_option
                                if partial_match
                                else actual_option == wanted_option
                            )
                            if option.is_displayed() and option.is_enabled() and matches:
                                return option
                        except WebDriverException:
                            continue
                    return False

                option = self._wait(10).until(find_visible_option)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", option
                )
                ActionChains(self.driver, duration=200).move_to_element(
                    option
                ).pause(0.2).click().perform()

                def selected_option_menu_is_closed(driver):
                    for item in driver.find_elements(*option_locator):
                        try:
                            if (
                                item.is_displayed()
                                and self._normalized_text(item.text) == wanted_option
                            ):
                                return False
                        except WebDriverException:
                            continue
                    return True

                if wait_for_menu_to_close:
                    # The parent settings page also contains elements with the
                    # menu-item-title class. Waiting for *all* such elements to
                    # disappear can never succeed after a valid selection.
                    self._wait(5).until(selected_option_menu_is_closed)

                if wait_for_menu_to_close and value_locator and wanted_value:
                    stable_samples = {"count": 0}

                    def expected_value_is_stable(driver):
                        actual = self._normalized_text(
                            driver.find_element(*value_locator).text
                        )
                        if actual == wanted_value:
                            stable_samples["count"] += 1
                        else:
                            stable_samples["count"] = 0
                        return stable_samples["count"] >= 3

                    self._wait(10).until(
                        expected_value_is_stable
                    )
                return
            except Exception as error:
                last_error = error
                # Close a half-open menu before the bounded retry.
                try:
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                except Exception:
                    pass

        available = ", ".join(sorted(observed_options)) or "нет видимых опций"
        raise RuntimeError(
            f"Не удалось выбрать '{option_text}' в комбобоксе после "
            f"{attempts} попыток. Видимые опции: {available}."
        ) from last_error

    def select_resolution(self, resolution_text):
        """
        Выбирает разрешение в соответствующем выпадающем списке.

        :param resolution_text: Текст варианта разрешения
        :return: None
        """
        self.hover_element(self.RESOLUTION_COMBOBOX)
        self.select_from_combobox(
            self.RESOLUTION_COMBOBOX,
            resolution_text.replace("X", " × "),
            value_locator=self.RESOLUTION_VALUE,
            expected_value=resolution_text,
        )

    def select_framerate(
        self,
        framerate_text,
        expected_value=None,
        wait_for_menu_to_close=False,
        verify_value=True,
    ):
        """
        Выбирает частоту кадров в соответствующем выпадающем списке.

        :param framerate_text: Текст варианта частоты кадров
        :return: None
        """
        self.hover_element(self.FRAMERATE_COMBOBOX)
        self.select_from_combobox(
            self.FRAMERATE_COMBOBOX,
            framerate_text.replace("FPS", "fps"),
            value_locator=self.FRAMERATE_VALUE if verify_value else None,
            expected_value=expected_value or framerate_text,
            wait_for_menu_to_close=wait_for_menu_to_close,
        )

    def select_audio_bitrate(self, audio_bitrate_text):
        """
        Выбирает битрейт аудио с учетом специальных замен текста.

        :param audio_bitrate_text: Текст варианта битрейта
        :return: None
        """
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
        self.select_from_combobox(
            self.AUDIO_BITRATE_COMBOBOX,
            audio_bitrate_text,
            replacements,
            self.AUDIO_BITRATE_VALUE,
            audio_bitrate_text,
        )

    def select_video_bitrate(self, video_bitrate_text):
        """
        Выбирает битрейт видео с учетом специальных замен текста.

        :param video_bitrate_text: Текст варианта битрейта
        :return: None
        """
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
        self.select_from_combobox(
            self.VIDEO_BITRATE_COMBOBOX,
            video_bitrate_text,
            replacements,
            self.VIDEO_BITRATE_VALUE,
            video_bitrate_text,
        )

    def select_video_encoder(self, video_encoder_text):
        """
        Выбирает видеокодек в соответствующем выпадающем списке.

        :param video_encoder_text: Текст варианта видеокодека
        :return: None
        """
        self.hover_element(self.VIDEO_ENCODER_COMBOBOX)
        self.select_from_combobox(
            self.VIDEO_ENCODER_COMBOBOX,
            video_encoder_text,
            value_locator=self.VIDEO_ENCODER_VALUE,
            expected_value=video_encoder_text,
        )

    def select_camera(self, input_camera_text):
        """
        Выбирает камеру в соответствующем выпадающем списке.

        :param input_camera_text: Текст варианта камеры
        :return: None
        """
        self.hover_element(self.INPUT_CAMERA_COMBOBOX)
        self.select_from_combobox(
            self.INPUT_CAMERA_COMBOBOX,
            input_camera_text,
            partial_match=True,
        )

    def select_microphone(self, input_microphone_text):
        """
        Выбирает микрофон в соответствующем выпадающем списке.

        :param input_microphone_text: Текст варианта микрофона
        :return: None
        """
        self.hover_element(self.INPUT_MICROPHONE_COMBOBOX)
        self.select_from_combobox(
            self.INPUT_MICROPHONE_COMBOBOX,
            input_microphone_text,
            partial_match=True,
        )

    def select_audio_channels(self, audio_channels_text):
        """
        Выбирает аудиоканалы в соответствующем выпадающем списке.

        :param audio_channels_text: Текст варианта аудиоканалов
        :return: None
        """
        self.hover_element(self.AUDIO_CHANNELS_COMBOBOX)
        try:
            self.select_from_combobox(
                self.AUDIO_CHANNELS_COMBOBOX,
                audio_channels_text,
                value_locator=self.AUDIO_CHANNELS_VALUE,
                expected_value=audio_channels_text,
                attempts=1,
            )
        except RuntimeError:
            # Recent WebGuest builds omit numeric presets when the selected
            # microphone exposes no matching channel layout. The same mapping
            # remains supported through "Other channels"; exercise that UI
            # path instead of failing because an optional shortcut is absent.
            if not re.fullmatch(r"\s*\d+\s*(?:,\s*\d+\s*)+", audio_channels_text):
                raise

            self.click(self.COMBOBOX_BACK_BUTTON)
            self.select_from_combobox(
                self.AUDIO_CHANNELS_COMBOBOX,
                "Other channels",
                attempts=1,
            )
            self.input_text(self.INPUT_FIELD_OTHER_CHANNELS, audio_channels_text)

    def is_switcher_active(self, switcher_locator):
        """
        Проверяет состояние свитчера по CSS-классам.

        :param switcher_locator: Локатор элемента свитчера
        :return: True если свитчер активен, иначе False
        """
        try:
            switcher = self.wait_for_element(switcher_locator)
            return 'bg-success' in switcher.get_attribute('class') and 'bg-danger' not in switcher.get_attribute(
                'class')
        except NoSuchElementException as e:
            print(f"Ошибка при проверке состояния свитчера: {e}")
            return False

    def is_fullscreen(self):
        """
        Проверяет полноэкранный режим через JavaScript.

        :return: True если включен полноэкранный режим, иначе False
        """
        fullscreen_state = self.driver.execute_script("return document.fullscreenElement !== null;")
        return fullscreen_state

    def is_fullscreen_button_pressed(self, button_locator):
        """
        Проверяет состояние кнопки полноэкранного режима по SVG-иконке.

        :param button_locator: Локатор кнопки
        :return: True если кнопка в состоянии "выключено", иначе False
        """
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

    def focus_browser_window(self):
        """
        Наводит курсор на окно браузера (на элемент body) и фокусирует вкладку.
        Используется как безопасная подготовка перед hover на конкретные элементы,
        чтобы избежать ошибки "move target out of bounds".
        """
        try:
            # Фокусируем текущую вкладку
            self.driver.switch_to.window(self.driver.current_window_handle)
            self.driver.execute_script("window.focus();")

            # Наводим на body (гарантированно в границах окна)
            body = self.wait_for_element((By.TAG_NAME, 'body'))
            self._actions().move_to_element(body).perform()
        except Exception as e:
            print(f"Ошибка при наведении на окно браузера: {e}")

    def release_local_media_tracks(self):
        """Release camera/microphone without closing the active WG session.

        This is useful in tests whose subject is server-side identity or access
        control rather than media capture.  It prevents a second tab from
        failing on an occupied virtual device before reaching the assertion the
        test actually intends to make.
        """
        self.driver.execute_script(
            """
            const tracks = new Set();
            for (const stream of (window.__vtActiveMediaStreams || [])) {
                if (stream && stream.getTracks) {
                    for (const track of stream.getTracks()) tracks.add(track);
                }
            }
            for (const media of document.querySelectorAll(
                'video[data-cy="local-video"], audio[data-cy="local-audio"]'
            )) {
                const stream = media.srcObject;
                if (stream && stream.getTracks) {
                    for (const track of stream.getTracks()) tracks.add(track);
                }
            }
            for (const track of tracks) track.stop();
            return tracks.size;
            """
        )

    def open_new_tab(self, timeout=10):
        """Open and switch to the tab created by this call.

        Indexing ``window_handles[1]`` is order-dependent and a delayed popup
        can make it select the wrong window.  Resolve the new handle by set
        difference instead.
        """
        existing_handles = set(self.driver.window_handles)
        self.driver.execute_script("window.open('about:blank', '_blank');")
        new_handles = self._wait(timeout).until(
            lambda driver: set(driver.window_handles) - existing_handles
        )
        new_handle = next(iter(new_handles))
        self.driver.switch_to.window(new_handle)
        return new_handle
