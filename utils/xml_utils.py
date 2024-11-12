# xml_utils.py
from lxml import etree


def read_and_print_xml(file_path, logger):
    try:
        # Загружаем XML файл
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Удаляем префиксы пространств имен
        content = content.replace('vt20:', '').replace('screen_capture:', '').replace('webrtc:', '').replace(
            'runtime:', '').replace('preview:', '').replace('venc_srt_props:', '').replace('device:', '').replace(
            'srt_props:', '')

        # Парсим XML с помощью lxml
        root = etree.fromstring(content.encode('utf-8'))

        # Рекурсивная функция для вывода элементов XML
        def print_element(element, level=0):
            indent = '  ' * level  # Уровень отступа
            tag = element.tag
            attributes = " ".join(f'{key}="{value}"' for key, value in element.attrib.items())  # Получаем атрибуты

            # Выводим тег и атрибуты
            if attributes:
                logger.info(f"{indent}<{tag} {attributes}>")
            else:
                logger.info(f"{indent}<{tag}>")

            # Выводим текстовое содержимое, если оно существует
            if element.text and element.text.strip():
                logger.info(f"{indent}  {element.text.strip()}")  # Выводим текст, если он есть

            # Рекурсивный вызов для дочерних элементов
            for child in element:
                print_element(child, level + 1)

            logger.info(f"{indent}</{tag}>")  # Закрывающий тег

        # Выводим корневой элемент
        print_element(root)

    except etree.XMLSyntaxError as e:
        logger.error(f"Ошибка при разборе XML: {e}")
    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
