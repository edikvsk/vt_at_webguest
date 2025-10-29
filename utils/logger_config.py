import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json


class ColoredFormatter(logging.Formatter):
    """Форматтер с поддержкой цветов для консольного вывода."""
    
    # Цветовые коды ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Добавляем цвет к уровню логирования
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            record.colored_levelname = f"{color}{record.levelname}{reset}"
        
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """Форматтер для структурированного JSON логирования."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Добавляем дополнительные поля если они есть
        if hasattr(record, 'test_step'):
            log_entry['test_step'] = record.test_step
        if hasattr(record, 'element_locator'):
            log_entry['element_locator'] = record.element_locator
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
            
        return json.dumps(log_entry, ensure_ascii=False)


class TestStepFilter(logging.Filter):
    """Фильтр для выделения шагов тестов."""
    
    def filter(self, record):
        # Помечаем записи, которые являются шагами тестов
        if hasattr(record, 'test_step') or 'шаг' in record.getMessage().lower():
            record.is_test_step = True
        return True


class LoggerManager:
    """Менеджер для управления логгерами."""
    
    def __init__(self):
        self.loggers: Dict[str, logging.Logger] = {}
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
    def setup_logger(
        self, 
        test_name: str, 
        level: int = logging.INFO,
        console_output: bool = False,  # Отключаем по умолчанию - pytest уже логирует в консоль
        file_output: bool = True,
        structured_logging: bool = False
    ) -> logging.Logger:
        """
        Настраивает и возвращает логгер для теста.
        
        Args:
            test_name: Имя теста
            level: Уровень логирования
            console_output: Выводить ли логи в консоль (False по умолчанию, так как pytest уже логирует)
            file_output: Сохранять ли логи в файл
            structured_logging: Использовать ли структурированное логирование
            
        Returns:
            Настроенный логгер
        """
        # Если логгер уже существует, возвращаем его
        if test_name in self.loggers:
            return self.loggers[test_name]
            
        logger = logging.getLogger(test_name)
        logger.setLevel(level)
        
        # Очищаем существующие обработчики
        logger.handlers.clear()
        
        # Запрещаем логгеру передавать сообщения выше по иерархии,
        # чтобы избежать дублирования с pytest логированием
        logger.propagate = True  # Оставляем True для pytest
        
        # Настройка консольного вывода (только если явно запрошено)
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            
            if structured_logging:
                console_formatter = StructuredFormatter()
            else:
                console_formatter = ColoredFormatter(
                    '\n%(asctime)s - %(name)s - %(colored_levelname)s - %(message)s'
                )
            
            console_handler.setFormatter(console_formatter)
            console_handler.addFilter(TestStepFilter())
            logger.addHandler(console_handler)
        
        # Настройка файлового вывода
        if file_output:
            # Создаем файл лога с временной меткой
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = self.log_dir / f"{test_name}_{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            
            if structured_logging:
                file_formatter = StructuredFormatter()
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            file_handler.setFormatter(file_formatter)
            file_handler.addFilter(TestStepFilter())
            logger.addHandler(file_handler)
        
        # Сохраняем логгер
        self.loggers[test_name] = logger
        
        logger.info(f"Логгер инициализирован для теста: {test_name}")
        return logger
    
    def get_logger(self, test_name: str) -> Optional[logging.Logger]:
        """Возвращает существующий логгер по имени."""
        return self.loggers.get(test_name)
    
    def log_test_step(self, logger: logging.Logger, step_description: str, **kwargs):
        """
        Логирует шаг теста с дополнительными метаданными.
        
        Args:
            logger: Логгер
            step_description: Описание шага
            **kwargs: Дополнительные метаданные
        """
        # Создаем LogRecord с дополнительными атрибутами
        record = logger.makeRecord(
            logger.name, logging.INFO, "", 0, step_description, (), None
        )
        
        # Добавляем дополнительные атрибуты
        record.test_step = True
        for key, value in kwargs.items():
            setattr(record, key, value)
            
        logger.handle(record)
    
    def log_element_interaction(
        self, 
        logger: logging.Logger, 
        action: str, 
        locator: str, 
        success: bool = True,
        duration: Optional[float] = None
    ):
        """
        Логирует взаимодействие с элементом.
        
        Args:
            logger: Логгер
            action: Действие (click, send_keys, etc.)
            locator: Локатор элемента
            success: Успешность операции
            duration: Длительность операции в секундах
        """
        level = logging.INFO if success else logging.ERROR
        message = f"{'✓' if success else '✗'} {action}: {locator}"
        
        if duration:
            message += f" ({duration:.2f}s)"
            
        record = logger.makeRecord(
            logger.name, level, "", 0, message, (), None
        )
        record.element_locator = locator
        record.action = action
        record.success = success
        if duration:
            record.duration = duration
            
        logger.handle(record)
    
    def create_test_report(self, test_name: str) -> Dict[str, Any]:
        """
        Создает отчет по логам теста.
        
        Args:
            test_name: Имя теста
            
        Returns:
            Словарь с информацией о тесте
        """
        logger = self.get_logger(test_name)
        if not logger:
            return {}
            
        # Здесь можно анализировать логи и создавать отчет
        # Пока возвращаем базовую информацию
        return {
            'test_name': test_name,
            'logger_level': logger.level,
            'handlers_count': len(logger.handlers),
            'timestamp': datetime.now().isoformat()
        }


# Глобальный экземпляр менеджера логгеров
logger_manager = LoggerManager()


def setup_logger(
    test_name: str, 
    level: int = logging.INFO,
    console_output: bool = False,  # Изменено по умолчанию
    file_output: bool = True,
    structured_logging: bool = False
) -> logging.Logger:
    """
    Функция для обратной совместимости.
    Настраивает логгер через LoggerManager.
    """
    # Получаем настройки из переменных окружения
    level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper(), logging.INFO)
    console_output = os.getenv('LOG_CONSOLE', 'false').lower() in ('true', '1', 'yes')  # Изменено на false
    file_output = os.getenv('LOG_FILE', 'false').lower() in ('true', '1', 'yes')
    structured_logging = os.getenv('LOG_STRUCTURED', 'false').lower() in ('true', '1', 'yes')
    
    return logger_manager.setup_logger(
        test_name=test_name,
        level=level,
        console_output=console_output,
        file_output=file_output,
        structured_logging=structured_logging
    )


def get_test_logger(test_name: str) -> Optional[logging.Logger]:
    """Возвращает существующий логгер для теста."""
    return logger_manager.get_logger(test_name)


def log_test_step(logger: logging.Logger, step_description: str, **kwargs):
    """Логирует шаг теста."""
    logger_manager.log_test_step(logger, step_description, **kwargs)


def log_element_interaction(
    logger: logging.Logger, 
    action: str, 
    locator: str, 
    success: bool = True,
    duration: Optional[float] = None
):
    """Логирует взаимодействие с элементом."""
    logger_manager.log_element_interaction(logger, action, locator, success, duration)
