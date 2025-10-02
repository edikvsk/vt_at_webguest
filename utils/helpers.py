import time
from functools import wraps
from typing import Any, Callable, Optional
import logging


def log_step(logger: logging.Logger, step_description: str, log_duration: bool = True):
    """
    Улучшенный декоратор для логирования шагов тестов с замером времени выполнения.
    
    Args:
        logger: Логгер для записи сообщений
        step_description: Описание шага теста
        log_duration: Логировать ли время выполнения
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            # Логируем начало шага
            logger.info(f"🔄 Начало: {step_description}")
            
            try:
                result = func(*args, **kwargs)
                
                # Вычисляем время выполнения
                duration = time.time() - start_time
                
                # Логируем успешное завершение
                if log_duration:
                    logger.info(f"✅ Завершен: {step_description} ({duration:.2f}с)")
                else:
                    logger.info(f"✅ Завершен: {step_description}")
                
                return result
                
            except Exception as e:
                # Вычисляем время до ошибки
                duration = time.time() - start_time
                
                # Логируем ошибку
                logger.error(f"❌ Ошибка на шаге '{step_description}' ({duration:.2f}с): {e}")
                raise  # Перекидываем исключение дальше

        return wrapper
    return decorator


def retry_on_failure(
    max_attempts: int = 3, 
    delay: float = 1.0, 
    exceptions: tuple = (Exception,),
    logger: Optional[logging.Logger] = None
):
    """
    Декоратор для повторного выполнения функции при ошибке.
    
    Args:
        max_attempts: Максимальное количество попыток
        delay: Задержка между попытками в секундах
        exceptions: Типы исключений для повтора
        logger: Логгер для записи сообщений
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if logger:
                        logger.warning(
                            f"Попытка {attempt}/{max_attempts} неуспешна для {func.__name__}: {e}"
                        )
                    
                    if attempt < max_attempts:
                        if logger:
                            logger.info(f"Ожидание {delay}с перед следующей попыткой...")
                        time.sleep(delay)
                    else:
                        if logger:
                            logger.error(f"Все {max_attempts} попыток исчерпаны для {func.__name__}")
                        raise last_exception
            
            # Этот код никогда не должен выполняться, но на всякий случай
            raise last_exception
            
        return wrapper
    return decorator


def measure_time(logger: Optional[logging.Logger] = None):
    """
    Декоратор для замера времени выполнения функции.
    
    Args:
        logger: Логгер для записи времени выполнения
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                if logger:
                    logger.debug(f"⏱️  {func.__name__} выполнена за {duration:.3f}с")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                if logger:
                    logger.debug(f"⏱️  {func.__name__} завершена с ошибкой за {duration:.3f}с")
                
                raise
                
        return wrapper
    return decorator


def conditional_skip(condition: Callable[[], bool], reason: str = "Условие не выполнено"):
    """
    Декоратор для условного пропуска выполнения функции.
    
    Args:
        condition: Функция, возвращающая True/False
        reason: Причина пропуска
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not condition():
                print(f"⏭️  Пропущено {func.__name__}: {reason}")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_function_call(logger: logging.Logger, log_args: bool = False):
    """
    Декоратор для логирования вызовов функций.
    
    Args:
        logger: Логгер
        log_args: Логировать ли аргументы функции
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if log_args:
                args_str = ", ".join([str(arg) for arg in args])
                kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
                all_args = ", ".join(filter(None, [args_str, kwargs_str]))
                logger.debug(f"📞 Вызов {func.__name__}({all_args})")
            else:
                logger.debug(f"📞 Вызов {func.__name__}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def safe_execute(
    default_return: Any = None, 
    logger: Optional[logging.Logger] = None,
    suppress_exceptions: tuple = (Exception,)
):
    """
    Декоратор для безопасного выполнения функции с возвратом значения по умолчанию при ошибке.
    
    Args:
        default_return: Значение по умолчанию при ошибке
        logger: Логгер для записи ошибок
        suppress_exceptions: Типы исключений для подавления
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except suppress_exceptions as e:
                if logger:
                    logger.warning(f"Безопасное выполнение {func.__name__} завершилось ошибкой: {e}")
                return default_return
        return wrapper
    return decorator


class StepManager:
    """Менеджер для управления шагами тестов."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.current_step = 0
        self.total_steps = 0
        self.failed_steps = []
        self.start_time = None
    
    def start_test(self, total_steps: int = 0):
        """Начинает выполнение теста."""
        self.total_steps = total_steps
        self.current_step = 0
        self.failed_steps = []
        self.start_time = time.time()
        
        if total_steps > 0:
            self.logger.info(f"🚀 Начало теста ({total_steps} шагов)")
        else:
            self.logger.info("🚀 Начало теста")
    
    def execute_step(self, step_description: str, step_function: Callable, *args, **kwargs):
        """
        Выполняет шаг теста.
        
        Args:
            step_description: Описание шага
            step_function: Функция для выполнения
            *args, **kwargs: Аргументы для функции
        """
        self.current_step += 1
        
        progress = ""
        if self.total_steps > 0:
            progress = f" [{self.current_step}/{self.total_steps}]"
        
        self.logger.info(f"🔄 Шаг {self.current_step}{progress}: {step_description}")
        
        start_time = time.time()
        try:
            result = step_function(*args, **kwargs)
            duration = time.time() - start_time
            self.logger.info(f"✅ Шаг {self.current_step} завершен ({duration:.2f}с)")
            return result
        except Exception as e:
            duration = time.time() - start_time
            self.failed_steps.append({
                'step': self.current_step,
                'description': step_description,
                'error': str(e),
                'duration': duration
            })
            self.logger.error(f"❌ Шаг {self.current_step} завершился ошибкой ({duration:.2f}с): {e}")
            raise
    
    def finish_test(self):
        """Завершает выполнение теста и выводит сводку."""
        if self.start_time:
            total_duration = time.time() - self.start_time
            
            if not self.failed_steps:
                self.logger.info(f"🎉 Тест успешно завершен за {total_duration:.2f}с")
            else:
                self.logger.error(
                    f"💥 Тест завершен с ошибками за {total_duration:.2f}с. "
                    f"Неуспешных шагов: {len(self.failed_steps)}/{self.current_step}"
                )
                
                for failed_step in self.failed_steps:
                    self.logger.error(
                        f"   - Шаг {failed_step['step']}: {failed_step['description']} "
                        f"({failed_step['error']})"
                    )
