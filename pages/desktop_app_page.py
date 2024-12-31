import re
import time

from pywinauto.findwindows import ElementNotFoundError


class DesktopAppPage:
    # Локаторы:

    VT_WEB_GUEST_SETTINGS = "Web Guest Settings"
    VT_OK_BUTTON = "OK"

    def __init__(self, main_window):
        self.main_window = main_window

    # Методы:
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

    def right_click_vt_source_item(self, title_part):
        """Выполняет правый клик на элементе с заданной частью заголовка."""
        try:
            text_element = self.main_window.child_window(title_re=f'.*{re.escape(title_part)}.*', control_type="Text")
            if text_element.exists() and text_element.is_enabled():
                text_element.click_input(button='right')
                time.sleep(1)  # Ждем появления контекстного меню
            else:
                raise ElementNotFoundError(f"Элемент с частью заголовка '{title_part}' не доступен для клика.")
        except Exception as e:
            raise RuntimeError(f"Ошибка при выполнении правого клика на элементе: {e}")

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

            time.sleep(0.5)

        raise ElementNotFoundError(f"Кнопка с именем '{button_name}' не доступна для клика в течение {timeout} секунд.")

    def click_vt_wg_settings_item(self, menu_item_title):
        """Кликает по элементу меню с заданным заголовком."""
        try:
            menu_item = self.main_window.child_window(title=menu_item_title, control_type="MenuItem")
            if menu_item.exists() and menu_item.is_enabled():
                menu_item.click_input()
            else:
                raise ElementNotFoundError(f"Элемент '{menu_item_title}' не доступен для клика.")
        except Exception as e:
            raise RuntimeError(f"Ошибка при клике на элемент меню '{menu_item_title}': {e}")

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

    def scroll_down_until_text_found(self, title_part, amount="line"):
        """Прокручивает вниз элемент DataItem до тех пор, пока не найдет элемент с текстом, соответствующим
        регулярному выражению."""
        try:
            # Получаем все элементы DataGrid
            data_grids = self.main_window.children(class_name="DataGrid")

            if not data_grids:
                raise RuntimeError("Элемент DataGrid не найден.")

            data_grid = data_grids[0]

            found = False
            scroll_count = 0  # Счетчик прокруток

            while not found:
                # Получаем все элементы DataItem внутри DataGrid
                data_items = data_grid.children(control_type="DataItem")

                for data_item in data_items:
                    # Ищем все элементы Custom внутри DataItem
                    custom_elements = data_item.children(control_type="Custom")

                    text_found_in_current_item = False  # Флаг для текущего DataItem

                    for custom_element in custom_elements:
                        # Ищем элемент Text внутри Custom
                        text_elements = custom_element.children(control_type="Text")

                        for text_element in text_elements:
                            text_content = text_element.window_text()
                            if re.search(f'.*{re.escape(title_part)}.*', text_content):
                                found = True
                                text_found_in_current_item = True
                                data_item.click_input()
                                break

                        if found:  # Если найден элемент, выходим из внутреннего цикла
                            break

                    if found:  # Если найден элемент, выходим из внешнего цикла
                        break

                    # Если текст не найден в текущем DataItem, прокручиваем вниз
                    if not text_found_in_current_item:
                        data_grid.scroll('down', amount)  # Прокрутка вниз на одну строку
                        scroll_count += 1

                # Проверяем, есть ли еще элементы для проверки
                if len(data_items) == 0:  # Если нет элементов для проверки, выходим из цикла
                    raise RuntimeError("Элементы DataItem не найдены, прокрутка завершена.")

        except Exception as e:
            raise RuntimeError(f"Ошибка при выполнении прокрутки вниз: {e}")

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
