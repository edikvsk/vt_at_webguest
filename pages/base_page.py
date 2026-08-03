import logging
from typing import List, Optional, Tuple, Union

from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains


class BasePage:
    """Базовый класс для всех страниц с общими методами взаимодействия с элементами."""
    
    DEFAULT_TIMEOUT = 10
    LONG_TIMEOUT = 20
    
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(self.__class__.__name__)

    def wait_for_element(self, locator: Tuple[By, str], timeout: int = None) -> Optional[WebElement]:
        """
        Ожидает появления элемента в DOM.
        
        Args:
            locator: Локатор элемента (By, value)
            timeout: Время ожидания в секундах
            
        Returns:
            WebElement или None если элемент не найден
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located(locator))
            self.logger.debug(f"Элемент найден: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"Элемент не найден за {timeout}с: {locator}")
            return None

    def wait_for_element_visible(self, locator: Tuple[By, str], timeout: int = None) -> Optional[WebElement]:
        """
        Ожидает появления и видимости элемента.
        
        Args:
            locator: Локатор элемента
            timeout: Время ожидания в секундах
            
        Returns:
            WebElement или None если элемент не найден/не виден
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located(locator))
            self.logger.debug(f"Элемент виден: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"Элемент не стал видимым за {timeout}с: {locator}")
            return None

    def wait_for_element_clickable(self, locator: Tuple[By, str], timeout: int = None) -> Optional[WebElement]:
        """
        Ожидает, пока элемент станет кликабельным.
        
        Args:
            locator: Локатор элемента
            timeout: Время ожидания в секундах
            
        Returns:
            WebElement или None если элемент не стал кликабельным
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable(locator))
            self.logger.debug(f"Элемент кликабелен: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"Элемент не стал кликабельным за {timeout}с: {locator}")
            return None

    def find_element(self, by: By, value: str, timeout: int = None) -> Optional[WebElement]:
        """
        Находит элемент по локатору.
        
        Args:
            by: Тип локатора
            value: Значение локатора
            timeout: Время ожидания
            
        Returns:
            WebElement или None
        """
        return self.wait_for_element((by, value), timeout)

    def find_elements(self, by: By, value: str, timeout: int = None) -> List[WebElement]:
        """
        Находит все элементы по локатору.
        
        Args:
            by: Тип локатора
            value: Значение локатора  
            timeout: Время ожидания
            
        Returns:
            Список WebElement (может быть пустым)
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            wait = WebDriverWait(self.driver, timeout)
            elements = wait.until(EC.presence_of_all_elements_located((by, value)))
            self.logger.debug(f"Найдено {len(elements)} элементов: {by}={value}")
            return elements
        except TimeoutException:
            self.logger.warning(f"Элементы не найдены за {timeout}с: {by}={value}")
            return []

    def send_keys(self, locator: Tuple[By, str], text: str, clear_first: bool = True, timeout: int = None) -> bool:
        """
        Вводит текст в элемент.
        
        Args:
            locator: Локатор элемента
            text: Текст для ввода
            clear_first: Очищать поле перед вводом
            timeout: Время ожидания
            
        Returns:
            True если успешно, False иначе
        """
        element = self.wait_for_element_clickable(locator, timeout)
        if element:
            try:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                self.logger.debug(f"Текст введен в {locator}: {text}")
                return True
            except Exception as e:
                self.logger.error(f"Ошибка ввода текста в {locator}: {e}")
        return False

    def click(self, locator: Tuple[By, str], timeout: int = None, scroll_to: bool = False) -> bool:
        """
        Кликает по элементу с улучшенной обработкой ошибок.
        
        Args:
            locator: Локатор элемента
            timeout: Время ожидания
            scroll_to: Прокручивать к элементу перед кликом
            
        Returns:
            True если клик успешен, False иначе
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        element = self.wait_for_element_clickable(locator, timeout)
        if element is None:
            # Controls in the responsive bottom toolbar may be present and
            # enabled while Selenium reports them as covered by the layout.
            # Resolve the real button and dispatch its DOM click instead of
            # silently allowing the test to continue with a closed panel.
            element = self.wait_for_element(locator, timeout)
            if element is None or element.get_attribute("disabled") is not None:
                return False
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', inline: 'center'});"
                    "arguments[0].click();",
                    element,
                )
                self.logger.debug(f"Клик через JS выполнен: {locator}")
                return True
            except Exception as js_error:
                self.logger.error(f"Ошибка JS клика по {locator}: {js_error}")
                return False

        try:
            if scroll_to:
                self.scroll_to_element(element)
            element.click()
            self.logger.debug(f"Клик выполнен: {locator}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка клика по {locator}: {e}")
            # Попытка клика через JavaScript как fallback
            try:
                self.driver.execute_script("arguments[0].click();", element)
                self.logger.debug(f"Клик через JS выполнен: {locator}")
                return True
            except Exception as js_error:
                self.logger.error(f"Ошибка JS клика по {locator}: {js_error}")
        return False

    def get_text(self, locator: Tuple[By, str], timeout: int = None) -> str:
        """
        Получает текст элемента.
        
        Args:
            locator: Локатор элемента
            timeout: Время ожидания
            
        Returns:
            Текст элемента или пустая строка
        """
        element = self.wait_for_element_visible(locator, timeout)
        if element:
            try:
                text = element.text
                self.logger.debug(f"Получен текст из {locator}: {text}")
                return text
            except Exception as e:
                self.logger.error(f"Ошибка получения текста из {locator}: {e}")
        return ""

    def get_attribute(self, locator: Tuple[By, str], attribute: str, timeout: int = None) -> str:
        """
        Получает значение атрибута элемента.
        
        Args:
            locator: Локатор элемента
            attribute: Имя атрибута
            timeout: Время ожидания
            
        Returns:
            Значение атрибута или пустая строка
        """
        element = self.wait_for_element(locator, timeout)
        if element:
            try:
                value = element.get_attribute(attribute) or ""
                self.logger.debug(f"Получен атрибут {attribute} из {locator}: {value}")
                return value
            except Exception as e:
                self.logger.error(f"Ошибка получения атрибута {attribute} из {locator}: {e}")
        return ""

    def get_element_value(self, locator: Tuple[By, str], timeout: int = None) -> str:
        """Получает значение элемента (атрибут value)."""
        return self.get_attribute(locator, "value", timeout)

    def is_element_present(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """
        Проверяет наличие элемента в DOM.
        
        Args:
            locator: Локатор элемента
            timeout: Время ожидания
            
        Returns:
            True если элемент присутствует, False иначе
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def is_element_visible(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """
        Проверяет видимость элемента.
        
        Args:
            locator: Локатор элемента
            timeout: Время ожидания
            
        Returns:
            True если элемент видим, False иначе
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def is_element_clickable(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """
        Проверяет, кликабелен ли элемент.
        
        Args:
            locator: Локатор элемента
            timeout: Время ожидания
            
        Returns:
            True если элемент кликабелен, False иначе
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
            return True
        except TimeoutException:
            return False

    def is_displayed(self, by: By, value: str, timeout: int = None) -> bool:
        """Проверяет отображение элемента (устаревший метод, используйте is_element_visible)."""
        return self.is_element_visible((by, value), timeout)

    def wait_for_url(self, url: str, timeout: int = None) -> bool:
        """
        Ожидает определенный URL.
        
        Args:
            url: Ожидаемый URL
            timeout: Время ожидания
            
        Returns:
            True если URL соответствует, False иначе
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_to_be(url))
            self.logger.debug(f"URL соответствует: {url}")
            return True
        except TimeoutException:
            current_url = self.driver.current_url
            self.logger.error(f"URL не соответствует. Ожидался: {url}, текущий: {current_url}")
            return False

    def wait_for_url_contains(self, url_part: str, timeout: int = None) -> bool:
        """
        Ожидает, пока URL будет содержать определенную часть.
        
        Args:
            url_part: Часть URL
            timeout: Время ожидания
            
        Returns:
            True если URL содержит часть, False иначе
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_contains(url_part))
            self.logger.debug(f"URL содержит: {url_part}")
            return True
        except TimeoutException:
            current_url = self.driver.current_url
            self.logger.error(f"URL не содержит '{url_part}'. Текущий URL: {current_url}")
            return False

    def scroll_to_element(self, element: WebElement) -> None:
        """
        Прокручивает страницу к элементу.
        
        Args:
            element: WebElement для прокрутки
        """
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.logger.debug("Прокрутка к элементу выполнена")
        except Exception as e:
            self.logger.error(f"Ошибка прокрутки к элементу: {e}")

    def hover(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """
        Наводит курсор на элемент.
        
        Args:
            locator: Локатор элемента
            timeout: Время ожидания
            
        Returns:
            True если наведение успешно, False иначе
        """
        element = self.wait_for_element_visible(locator, timeout)
        if element:
            try:
                ActionChains(self.driver).move_to_element(element).perform()
                self.logger.debug(f"Наведение на элемент: {locator}")
                return True
            except Exception as e:
                self.logger.error(f"Ошибка наведения на {locator}: {e}")
        return False

    def double_click(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """
        Выполняет двойной клик по элементу.
        
        Args:
            locator: Локатор элемента
            timeout: Время ожидания
            
        Returns:
            True если двойной клик успешен, False иначе
        """
        element = self.wait_for_element_clickable(locator, timeout)
        if element:
            try:
                ActionChains(self.driver).double_click(element).perform()
                self.logger.debug(f"Двойной клик по элементу: {locator}")
                return True
            except Exception as e:
                self.logger.error(f"Ошибка двойного клика по {locator}: {e}")
        return False

    def right_click(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """
        Выполняет правый клик по элементу.
        
        Args:
            locator: Локатор элемента
            timeout: Время ожидания
            
        Returns:
            True если правый клик успешен, False иначе
        """
        element = self.wait_for_element_clickable(locator, timeout)
        if element:
            try:
                ActionChains(self.driver).context_click(element).perform()
                self.logger.debug(f"Правый клик по элементу: {locator}")
                return True
            except Exception as e:
                self.logger.error(f"Ошибка правого клика по {locator}: {e}")
        return False
