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
    def right_click_vt_source_item(self, title_part):
        """Выполняет правый клик на элементе с заданной частью заголовка."""
        try:
            # Используем регулярное выражение для поиска по части текста
            text_element = self.main_window.child_window(title_re=f'.*{re.escape(title_part)}.*', control_type="Text")
            if text_element.exists() and text_element.is_enabled():
                text_element.click_input(button='right')
                time.sleep(1)  # Ждем появления контекстного меню
            else:
                raise ElementNotFoundError(f"Элемент с частью заголовка '{title_part}' не доступен для клика.")
        except Exception as e:
            print(f"Ошибка при выполнении правого клика на элементе с частью заголовка '{title_part}': {e}")

    def click_vt_source_item(self, menu_item_title):
        """ Кликает по элементу меню с заданным заголовком."""
        try:
            menu_item = self.main_window.child_window(title=menu_item_title, control_type="MenuItem")
            if menu_item.exists() and menu_item.is_enabled():
                menu_item.click_input()
            else:
                raise ElementNotFoundError(f"Элемент '{menu_item_title}' не доступен для клика.")
        except Exception as e:
            print(f"Ошибка при клике на элемент меню '{menu_item_title}': {e}")

    def click_button_by_name(self, button_name):
        """ Кликает по кнопке с заданным именем. """
        try:
            button = self.main_window.child_window(title=button_name, control_type="Button")
            if button.exists() and button.is_enabled():
                button.click_input()
            else:
                raise ElementNotFoundError(f"Кнопка с именем '{button_name}' не доступна для клика.")
        except Exception as e:
            print(f"Ошибка при клике на кнопку с именем '{button_name}': {e}")

    def click_vt_wg_settings_item(self, menu_item_title):
        """ Кликает по элементу меню с заданным заголовком."""
        try:
            menu_item = self.main_window.child_window(title=menu_item_title, control_type="MenuItem")
            if menu_item.exists() and menu_item.is_enabled():
                menu_item.click_input()
            else:
                raise ElementNotFoundError(f"Элемент '{menu_item_title}' не доступен для клика.")
        except Exception as e:
            print(f"Ошибка при клике на элемент меню '{menu_item_title}': {e}")

    def get_vt_wg_settings_field_value(self, index):
        """ Получает значение поля в WebGuest Settings по заданному индексу."""
        try:
            edit_box = self.main_window.child_window(control_type="Edit", found_index=index)
            if edit_box.exists() and edit_box.is_enabled():
                value = edit_box.get_value()
                return value
            else:
                raise ElementNotFoundError(f"Элемент поля редактора с индексом {index} не найден или недоступен.")
        except Exception as e:
            print(f"Ошибка при получении значения поля редактора с индексом {index}: {e}")
            return None
