from lxml import etree


class XMLReader:
    def __init__(self, file_path, logger):  # Исправлено init на __init__
        self.file_path = file_path
        self.logger = logger

    def read_and_print(self):
        try:
            # Загружаем XML файл
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Удаляем префиксы пространств имен
            content = content.replace('vt20:', '').replace('screen_capture:', '').replace('webrtc:', '').replace(
                'runtime:', '').replace('preview:', '').replace('venc_srt_props:', '').replace('device:', '').replace(
                'srt_props:', '')

            # Парсим XML с помощью lxml
            root = etree.fromstring(content.encode('utf-8'))

            # Рекурсивная функция для вывода элементов XML
            self._print_element(root)

        except etree.XMLSyntaxError as e:
            self.logger.error(f"Ошибка при разборе XML: {e}")
        except FileNotFoundError:
            self.logger.error(f"Файл не найден: {self.file_path}")
        except Exception as e:
            self.logger.error(f"Произошла ошибка: {e}")

    def _print_element(self, element, level=0):
        indent = '  ' * level
        tag = element.tag
        attributes = " ".join(f'{key}="{value}"' for key, value in element.attrib.items())  # Получаем атрибуты

        # Выводим тег и атрибуты
        if attributes:
            self.logger.info(f"{indent}<{tag} {attributes}>")
        else:
            self.logger.info(f"{indent}<{tag}>")

        # Выводим текстовое содержимое, если оно существует
        if element.text and element.text.strip():
            self.logger.info(f"{indent}  {element.text.strip()}")

        # Рекурсивный вызов для дочерних элементов
        for child in element:
            self._print_element(child, level + 1)

        self.logger.info(f"{indent}</{tag}>")  # Закрывающий тег

    def find_channel_by_label(self, label):
        try:
            # Загружаем XML файл
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Удаляем префиксы пространств имен
            content = content.replace('vt20:', '').replace('screen_capture:', '').replace('webrtc:', '').replace(
                'runtime:', '').replace('preview:', '').replace('venc_srt_props:', '').replace('device:', '').replace(
                'srt_props:', '')

            # Парсим XML с помощью lxml
            root = etree.fromstring(content.encode('utf-8'))

            # Ищем элемент channel с нужным channel_label
            channels = root.findall('.//channel[@channel_label="{}"]'.format(label))
            if channels:
                # Если вы хотите вернуть только первый найденный канал
                channel = channels[0]
                channel_label = channel.attrib.get('channel_label', None)  # Извлекаем channel_label
                return channel_label  # Возвращаем channel_label
            else:
                self.logger.info(f"Канал с label '{label}' не найден.")
                return None  # Возвращаем None, если канал не найден
        except etree.XMLSyntaxError as e:
            self.logger.error(f"Ошибка при разборе XML: {e}")
            return None
        except FileNotFoundError:
            self.logger.error(f"Файл не найден: {self.file_path}")
            return None
        except Exception as e:
            self.logger.error(f"Произошла ошибка: {e}")
            return None
