import re
import time

from pywinauto.findwindows import ElementNotFoundError


class DesktopAppPage:
    # Локаторы:

    VT_WEB_GUEST_SETTINGS = "Web Guest Settings"
    VT_SECURITY_SETTINGS = "Security Settings"
    VT_SOURCE_SETTINGS = "Settings"
    VT_CLOSE_BUTTON = "PART_Close"
    VT_OK_BUTTON = "OK"

    def __init__(self, main_window):
        self.main_window = main_window

    # Методы:

    @staticmethod
    def click_button_in_window(window, automation_id, timeout=10):
        """
        Кликает по кнопке с заданным automation_id внутри указанного окна, ожидая её доступности.

        :param window: Окно (WindowSpecification), внутри которого нужно найти кнопку.
        :param automation_id: Automation ID кнопки.
        :param timeout: Время ожидания в секундах (по умолчанию 10).
        :raises ElementNotFoundError: Если кнопка не найдена или недоступна для клика в течение timeout секунд.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Ищем кнопку внутри указанного окна
            button = window.child_window(auto_id=automation_id, control_type="Button")

            if button.exists() and button.is_enabled():
                button.click_input()
                return
        raise ElementNotFoundError(
            f"Кнопка с automation_id '{automation_id}' внутри окна '{window.window_text()}' "
            f"не доступна для клика в течение {timeout} секунд."
        )

    @staticmethod
    def click_data_item_in_window(window, name, timeout=10):
        """
        Кликает по элементу с заданным именем (name) внутри указанного окна, ожидая его доступности.
        :param window: Окно (WindowSpecification), внутри которого нужно найти элемент.
        :param name: Имя (name) элемента.
        :param timeout: Время ожидания в секундах (по умолчанию 10).
        :raises ElementNotFoundError: Если элемент не найден или недоступен для клика в течение timeout секунд.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Ищем элемент внутри указанного окна по его имени и классу DataItem
            data_item = window.child_window(title=name, control_type="DataItem")
            if data_item.exists() and data_item.is_enabled():
                data_item.click_input()
                return
        raise ElementNotFoundError(
            f"Элемент с именем '{name}' и классом 'DataItem' внутри окна '{window.window_text()}' "
            f"не доступен для клика в течение {timeout} секунд."
        )

    def check_element_enabled_by_title_part(self, title_part):
        """Проверяет, доступен ли элемент с заданной частью заголовка."""
        try:
            text_element = self.main_window.child_window(title_re=f'.*{re.escape(title_part)}.*', control_type="Text")
            if text_element.exists() and text_element.is_enabled():
                return True
            else:
                return False
        except Exception as e:
            raise RuntimeError(f"Ошибка при проверке доступности элемента: {e}")

    def check_element_exists_by_title_part(self, title_part):
        """Проверяет наличие элемента с заданной частью заголовка."""
        try:
            text_element = self.main_window.child_window(title_re=f'.*{re.escape(title_part)}.*', control_type="Text")
            if text_element.exists():
                return True
            else:
                return False
        except Exception as e:
            raise RuntimeError(f"Ошибка при проверке наличия элемента: {e}")

    def right_click_vt_source_item(self, title_part, max_attempts=2):
        """Выполняет правый клик на элементе с заданной частью заголовка."""
        attempts = 0

        while attempts < max_attempts:
            try:
                text_element = self.main_window.child_window(title_re=f'.*{re.escape(title_part)}.*',
                                                             control_type="Text")
                if text_element.exists() and text_element.is_enabled():
                    parent = text_element.parent()  # Получаем родительский элемент
                    parent.set_focus()
                    text_element.click_input()
                    text_element.click_input(button='right')
                    return  # Успешный клик, выходим из метода
                else:
                    raise ElementNotFoundError(f"Элемент с частью заголовка '{title_part}' не доступен для клика.")
            except Exception as e:
                attempts += 1
                if attempts >= max_attempts:
                    raise RuntimeError(
                        f"Ошибка при выполнении правого клика на элементе после {max_attempts} попыток: {e}")

    def focus_click_vt_source_item(self, title_part, max_attempts=2):
        """Выполняет клик на элементе с заданной частью заголовка."""
        attempts = 0

        while attempts < max_attempts:
            try:
                text_element = self.main_window.child_window(title_re=f'.*{re.escape(title_part)}.*',
                                                             control_type="Text")
                if text_element.exists() and text_element.is_enabled():
                    # Прокручиваем к элементу
                    parent = text_element.parent()  # Получаем родительский элемент
                    parent.set_focus()  # Устанавливаем фокус на родительский элемент

                    # Выполняем клик на элементе
                    text_element.click_input()
                    return  # Успешный клик, выходим из метода
                else:
                    raise ElementNotFoundError(f"Элемент с частью заголовка '{title_part}' не доступен для клика.")
            except Exception as e:
                attempts += 1
                if attempts >= max_attempts:
                    raise RuntimeError(f"Ошибка при выполнении клика на элементе после {max_attempts} попыток: {e}")

    def click_vt_source_item(self, menu_item_title):
        """Кликает по элементу меню с заданным заголовком."""
        try:
            menu_item = self.main_window.child_window(title=menu_item_title, control_type="MenuItem")
            if menu_item.exists() and menu_item.is_enabled():
                menu_item.click_input()
            else:
                raise ElementNotFoundError(f"Элемент '{menu_item_title}' не доступен для клика.")
        except Exception as e:
            raise RuntimeError(f"Ошибка при клике на элемент меню '{menu_item_title}': {e}")

    def click_button_by_name(self, button_name, timeout=10):
        """Кликает по кнопке с заданным именем, ожидая её доступности."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            button = self.main_window.child_window(title=button_name, control_type="Button")

            if button.exists() and button.is_enabled():
                button.click_input()
                return

        raise ElementNotFoundError(f"Кнопка с именем '{button_name}' не доступна для клика в течение {timeout} секунд.")

    def find_window_by_title_substring(self, title_substring, timeout=10):
        """
        Находит окно, название которого содержит указанную подстроку.

        :param title_substring: Подстрока, которая должна содержаться в названии окна.
        :param timeout: Время ожидания в секундах (по умолчанию 10).
        :raises ElementNotFoundError: Если окно не найдено в течение timeout секунд.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Ищем окно по частичному совпадению заголовка
            window = self.main_window.child_window(title_re=f".*{title_substring}.*", control_type="Window")
            if window.exists():
                return window
        raise ElementNotFoundError(
            f"Окно, содержащее '{title_substring}' в названии, не найдено в течение {timeout} секунд.")

    def get_vt_wg_settings_field_value(self, index):
        """Получает значение поля в WebGuest Settings по заданному индексу."""
        try:
            edit_box = self.main_window.child_window(control_type="Edit", found_index=index)
            if edit_box.exists() and edit_box.is_enabled():
                value = edit_box.get_value()
                return value
            else:
                raise ElementNotFoundError(f"Элемент поля с индексом {index} не найден или недоступен.")
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении значения поля с индексом {index}: {e}")

    def set_vt_wg_settings_field_value(self, index, text):
        """
        Заполняет текстом поле в WebGuest Settings по заданному индексу.

        :param index: Индекс поля для заполнения.
        :param text: Текст, который нужно ввести в поле.
        :raises ElementNotFoundError: Если элемент не найден или недоступен.
        :raises RuntimeError: Если произошла ошибка при установке значения.
        """
        try:
            # Находим элемент по индексу
            edit_box = self.main_window.child_window(control_type="Edit", found_index=index)

            # Проверяем, существует ли элемент и доступен ли он для взаимодействия
            if edit_box.exists() and edit_box.is_enabled():
                # Очищаем поле перед вводом нового значения (опционально)
                edit_box.set_focus()
                edit_box.set_text('')  # Очистка поля

                # Вводим текст
                edit_box.type_keys(text, with_spaces=True)  # Используем type_keys для ввода текста
                return True
            else:
                raise ElementNotFoundError(f"Элемент поля с индексом {index} не найден или недоступен.")
        except Exception as e:
            raise RuntimeError(f"Ошибка при заполнении поля с индексом {index}: {e}")

    def get_combobox_item_name_by_index(self, combo_index, item_index):
        """Возвращает текст элемента в ComboBox по заданным индексам."""
        try:
            # Находим ComboBox по индексу
            combo_box = self.main_window.child_window(control_type="ComboBox", found_index=combo_index)
            if combo_box.exists() and combo_box.is_enabled():
                # Открываем ComboBox
                combo_box.click_input()

                # Получаем элемент списка по индексу
                list_item = combo_box.child_window(control_type="ListItem", found_index=item_index)

                if list_item.exists():
                    # Возвращаем текст элемента
                    return list_item.texts()
                else:
                    raise ElementNotFoundError(
                        f"Элемент с индексом {item_index} не найден в ComboBox с индексом {combo_index}.")
            else:
                raise ElementNotFoundError(f"ComboBox с индексом {combo_index} не найден или недоступен.")
        except Exception as e:
            raise RuntimeError(
                f"Ошибка при получении текста в ComboBox с индексом {combo_index} и элементом {item_index}: {e}")

    def select_combobox_item_by_index(self, combo_index, item_index):
        """Выбирает элемент в ComboBox по заданным индексам."""
        try:
            # Находим ComboBox по индексу
            combo_box = self.main_window.child_window(control_type="ComboBox", found_index=combo_index)
            if combo_box.exists() and combo_box.is_enabled():
                # Открываем ComboBox
                combo_box.click_input()

                # Получаем список элементов
                list_items = combo_box.child_window(control_type="ListItem", found_index=item_index)

                # Нажимаем на элемент
                list_items.click_input()
            else:
                raise ElementNotFoundError(f"ComboBox с индексом {combo_index} не найден или недоступен.")
        except Exception as e:
            raise RuntimeError(
                f"Ошибка при выборе элемента в ComboBox с индексом {combo_index} и элементом {item_index}: {e}")

    def get_vt_wg_button_state(self, index):
        """Получает состояние кнопки по заданному индексу."""
        try:
            button = self.main_window.child_window(control_type="Button", found_index=index)
            if button.exists() and button.is_enabled():
                state = button.get_toggle_state()
                return state
            else:
                raise ElementNotFoundError(f"Элемент кнопки с индексом {index} не найден или недоступен.")
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении состояния кнопки с индексом {index}: {e}")

    def toggle_vt_wg_button(self, index):
        """Переключает состояние кнопки в WebGuest Settings по заданному индексу."""
        try:
            button = self.main_window.child_window(control_type="Button", found_index=index)
            if button.exists() and button.is_enabled():
                button.toggle()  # Щелкаем по кнопке для переключения состояния
                print(f"Состояние кнопки с индексом {index} переключено.")
            else:
                raise ElementNotFoundError(f"Элемент кнопки с индексом {index} не найден или недоступен.")
        except Exception as e:
            raise RuntimeError(f"Ошибка при переключении состояния кнопки с индексом {index}: {e}")

    def select_combobox_item_by_numeric(self, combo_index, item_index):
        try:
            # Находим ComboBox по индексу
            combo_box = self.main_window.child_window(control_type="ComboBox", found_index=combo_index)
            if combo_box.exists() and combo_box.is_enabled():
                # Открываем ComboBox
                combo_box.click_input()

                # Получаем список элементов
                list_items = combo_box.child_window(control_type="ListItem", found_index=item_index)

                # Нажимаем на элемент
                list_items.click_input()
            else:
                raise ElementNotFoundError(f"ComboBox с индексом {combo_index} не найден или недоступен.")
        except Exception as e:
            raise RuntimeError(
                f"Ошибка при выборе элемента в ComboBox с индексом {combo_index} и элементом {item_index}: {e}")

    def get_combobox_item_text_by_index(self, combo_index, item_index):
        """Возвращает текст элемента в ComboBox по заданным индексам."""
        try:
            # Находим ComboBox по индексу
            combo_box = self.main_window.child_window(control_type="ComboBox", found_index=combo_index)
            if combo_box.exists() and combo_box.is_enabled():
                # Открываем ComboBox
                combo_box.click_input()

                # Получаем элемент списка по индексу
                list_item = combo_box.child_window(control_type="ListItem", found_index=item_index)

                if list_item.exists():
                    # Возвращаем текст элемента
                    return list_item.texts()
                else:
                    raise ElementNotFoundError(
                        f"Элемент с индексом {item_index} не найден в ComboBox с индексом {combo_index}.")
            else:
                raise ElementNotFoundError(f"ComboBox с индексом {combo_index} не найден или недоступен.")
        except Exception as e:
            raise RuntimeError(
                f"Ошибка при получении текста в ComboBox с индексом {combo_index} и элементом {item_index}: {e}")
