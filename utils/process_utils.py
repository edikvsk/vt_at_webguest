import logging
import subprocess
import time

import psutil

BAT_FILE_PATH = r"C:\Users\Demo\Desktop\VT builds\start_vt.bat"
PROCESS_NAME = "VT_Publisher.exe"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_process_running(process_name):
    """Проверяет, запущен ли процесс с заданным именем."""
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'].lower() == process_name.lower():
            return proc  # Возвращаем объект процесса
    return None


def run_vt_from_bat():
    """Функция для запуска BAT файла, если процесс не запущен."""
    if not is_process_running(PROCESS_NAME):
        try:
            subprocess.Popen(BAT_FILE_PATH, shell=True)
            time.sleep(10)
            logger.info(f"{PROCESS_NAME} был запущен.")
        except Exception as e:
            logger.error(f"Ошибка при запуске BAT файла: {e}")
    else:
        logger.info(f"{PROCESS_NAME} уже запущен. BAT файл не будет запущен.")


def kill_process(process_name):
    """Завершает процесс с заданным именем."""
    process = is_process_running(process_name)
    if process:
        try:
            process.terminate()  # Рассмотреть process.kill() для принудительного завершения
            process.wait()  # Ждем завершения процесса
            logger.info(f"Процесс '{process_name}' завершен.")
        except psutil.NoSuchProcess:
            logger.info("Процесс уже завершен.")
        except psutil.AccessDenied:
            logger.warning("Нет доступа для завершения процесса.")
        except Exception as e:
            logger.error(f"Ошибка при завершении процесса: {e}")
    else:
        logger.info(f"Процесс '{process_name}' не найден.")
