from functools import wraps


def log_step(logger, step_description):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(step_description)
            try:
                result = func(*args, **kwargs)
                logger.info(f"Завершен шаг: {step_description}")
                return result
            except Exception as e:
                logger.error(f"Ошибка на шаге '{step_description}': {e}")
                raise  # Перекидываем исключение дальше

        return wrapper

    return decorator
