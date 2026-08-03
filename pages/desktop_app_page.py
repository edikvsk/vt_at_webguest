import time

from pywinauto.findwindows import ElementNotFoundError
from pywinauto.mouse import click


class DesktopAppPage:
    # Локаторы:

    VT_WEB_GUEST_SETTINGS = "Web Guest Settings"
    VT_SECURITY_SETTINGS = "Security Settings"
    VT_SOURCE_SETTINGS = "Settings"
    VT_CLOSE_BUTTON = "PART_Close"
    VT_OK_BUTTON = "OK"

    def __init__(self, main_window):
        self.main_window = main_window

    @staticmethod
    def _element_state(element):
        """Return UIA state without allowing a stale element to break discovery."""
        try:
            visible = bool(element.is_visible())
        except Exception:
            visible = False
        try:
            enabled = bool(element.is_enabled())
        except Exception:
            enabled = False
        try:
            rectangle = element.rectangle()
            has_size = rectangle.width() > 0 and rectangle.height() > 0
        except Exception:
            rectangle = None
            has_size = False
        return visible, enabled, has_size, rectangle

    def _matching_text_elements(self, title_part):
        """Find every text control containing title_part without assuming uniqueness."""
        needle = title_part.strip().casefold()
        matches = []
        for element in self.main_window.descendants(control_type="Text"):
            try:
                title = element.window_text().strip()
            except Exception:
                continue
            if needle in title.casefold():
                matches.append((element, title))
        return matches

    def _find_text_element(self, title_part, enabled_only=False):
        """Resolve duplicate WPF text controls to the visible actionable instance."""
        matches = self._matching_text_elements(title_part)
        if not matches:
            raise ElementNotFoundError(
                f"No text element containing '{title_part}' was found in VT Publisher."
            )

        needle = title_part.strip().casefold()
        ranked = []
        for index, (element, title) in enumerate(matches):
            visible, enabled, has_size, rectangle = self._element_state(element)
            if enabled_only and not enabled:
                continue

            parent_actionable = False
            try:
                parent = element.parent()
                parent_visible, parent_enabled, parent_has_size, _ = self._element_state(parent)
                parent_actionable = parent_visible and parent_enabled and parent_has_size
            except Exception:
                pass

            # Visible, enabled controls with an actionable parent beat WPF template
            # duplicates. Among them, exact labels beat status/detail labels.
            score = (
                visible,
                enabled,
                has_size,
                parent_actionable,
                title.casefold() == needle,
                -index,
            )
            ranked.append((score, element, title, rectangle))

        if not ranked:
            raise ElementNotFoundError(
                f"Text element containing '{title_part}' exists but is not enabled."
            )

        ranked.sort(key=lambda candidate: candidate[0], reverse=True)
        _, selected, selected_title, selected_rectangle = ranked[0]
        if len(matches) > 1:
            print(
                f"Resolved {len(matches)} VT controls containing '{title_part}' to "
                f"'{selected_title}' at {selected_rectangle}."
            )
        return selected

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
            return any(
                self._element_state(element)[1]
                for element, _ in self._matching_text_elements(title_part)
            )
        except Exception as e:
            raise RuntimeError(f"Ошибка при проверке доступности элемента: {e}")

    def check_element_exists_by_title_part(self, title_part):
        """Проверяет наличие элемента с заданной частью заголовка."""
        try:
            return bool(self._matching_text_elements(title_part))
        except Exception as e:
            raise RuntimeError(f"Ошибка при проверке наличия элемента: {e}")

    def right_click_vt_source_item(self, title_part, max_attempts=2):
        """Выполняет правый клик на элементе с заданной частью заголовка."""
        attempts = 0

        while attempts < max_attempts:
            try:
                text_element = self._find_text_element(title_part, enabled_only=True)
                parent = text_element.parent()  # Получаем родительский элемент
                parent.set_focus()
                text_element.click_input()
                text_element.click_input(button='right')
                return  # Успешный клик, выходим из метода
            except Exception as e:
                attempts += 1
                if attempts >= max_attempts:
                    raise RuntimeError(
                        f"Ошибка при выполнении правого клика на элементе после {max_attempts} попыток: {e}")
                time.sleep(0.5)

    def focus_click_vt_source_item(self, title_part, max_attempts=2):
        """Выполняет клик на элементе с заданной частью заголовка."""
        attempts = 0

        while attempts < max_attempts:
            try:
                text_element = self._find_text_element(title_part, enabled_only=True)
                # Прокручиваем к элементу
                parent = text_element.parent()  # Получаем родительский элемент
                parent.set_focus()  # Устанавливаем фокус на родительский элемент

                # Выполняем клик на элементе
                text_element.click_input()
                return  # Успешный клик, выходим из метода
            except Exception as e:
                attempts += 1
                if attempts >= max_attempts:
                    raise RuntimeError(f"Ошибка при выполнении клика на элементе после {max_attempts} попыток: {e}")
                time.sleep(0.5)

    def click_vt_source_item(self, menu_item_title, timeout=10):
        """Wait for and click a VT context-menu item.

        WPF context menus are separate popup windows. Depending on timing,
        pywinauto may expose the popup under the main window or as another
        top-level window owned by the VT process. Search both locations until
        the item is actually visible and enabled instead of sampling once
        immediately after the right-click.
        """
        deadline = time.time() + timeout
        last_error = None

        while time.time() < deadline:
            roots = [self.main_window]
            try:
                roots.extend(self.main_window.app.windows())
            except Exception as error:
                last_error = error

            for root in roots:
                try:
                    menu_item = root.child_window(
                        title=menu_item_title,
                        control_type="MenuItem",
                    )
                    if (
                        menu_item.exists(timeout=0.2)
                        and menu_item.is_visible()
                        and menu_item.is_enabled()
                    ):
                        menu_item.click_input()
                        return
                except Exception as error:
                    last_error = error

            time.sleep(0.1)

        detail = f": {last_error}" if last_error else ""
        raise RuntimeError(
            f"Menu item '{menu_item_title}' did not become visible and "
            f"enabled within {timeout}s{detail}"
        )

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

    def mouse_click_vt_wg_button(self, index):
        """Переключает состояние кнопки в WebGuest Settings по заданному индексу."""
        try:
            button = self.main_window.child_window(control_type="Button", found_index=index)
            if button.exists() and button.is_enabled():
                rect = button.rectangle()  # Получаем координаты кнопки
                x, y = (rect.left + rect.width() // 2, rect.top + rect.height() // 2)  # Центр кнопки
                click(coords=(x, y))  # Кликаем по центру кнопки
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

    def select_combobox_item_by_name(self, combo_index, item_text, exact_match=True, timeout=10):
        """Выбирает элемент в ComboBox по названию (тексту).

        :param combo_index: Индекс ComboBox в окне
        :param item_text: Текст элемента для выбора
        :param exact_match: Если True — ищет точное совпадение; иначе допускает частичное
        :param timeout: Время ожидания
        """
        start_time = time.time()
        try:
            combo_box = self.main_window.child_window(control_type="ComboBox", found_index=combo_index)
            if not (combo_box.exists() and combo_box.is_enabled()):
                raise ElementNotFoundError(f"ComboBox с индексом {combo_index} не найден или недоступен.")

            combo_box.click_input()

            # Собираем все элементы списка
            items = []
            while time.time() - start_time < timeout:
                try:
                    # pywinauto: получить все ListItem под комбобоксом
                    items = combo_box.descendants(control_type="ListItem")
                    if items:
                        break
                except Exception:
                    pass
                time.sleep(0.2)

            if not items:
                raise ElementNotFoundError("Элементы списка в ComboBox не найдены.")

            target = None
            text_lower = item_text.lower()

            # Сначала точное совпадение по видимому тексту
            if exact_match:
                for it in items:
                    try:
                        texts = (it.texts() or [])
                        if any(t.lower() == text_lower for t in texts):
                            target = it
                            break
                    except Exception:
                        continue

            # Если не нашли, пробуем частичное совпадение
            if target is None:
                for it in items:
                    try:
                        texts = (it.texts() or [])
                        if any(text_lower in t.lower() for t in texts):
                            target = it
                            break
                    except Exception:
                        continue

            if target and target.is_enabled():
                target.click_input()
            else:
                raise ElementNotFoundError(f"Элемент с текстом '{item_text}' не найден или недоступен.")
        except Exception as e:
            raise RuntimeError(
                f"Ошибка при выборе элемента по имени в ComboBox с индексом {combo_index}: {e}")
