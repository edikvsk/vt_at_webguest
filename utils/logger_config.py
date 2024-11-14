import logging
import sys


class CustomErrorFilter(logging.Filter):
    def filter(self, record):
        if record.levelname == "ERROR":
            record.levelname = "ERROR__"
        return True


def setup_logger(test_name):
    logger = logging.getLogger(test_name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('\n%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Добавляем фильтр для изменения уровня логирования
    handler.addFilter(CustomErrorFilter())

    logger.addHandler(handler)
    return logger
