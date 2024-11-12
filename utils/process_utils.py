import subprocess
import time

import psutil

from utils.logger_config import setup_logger


class ProcessManager:
    def __init__(self, process_path, process_name):
        self.process_path = process_path
        self.process_name = process_name
        self.logger = setup_logger(self.process_name)

    def is_process_running(self):
        """Проверяет, запущен ли процесс с заданным именем."""
        for proc in psutil.process_iter(attrs=['name']):
            if proc.info['name'].lower() == self.process_name.lower():
                return proc  # Возвращаем объект процесса
        return None

    def start_process(self):
        """Запускает процесс, если он не запущен."""
        if not self.is_process_running():
            try:
                subprocess.Popen(self.process_path)  # Запускаем процесс напрямую
                time.sleep(15)  # Задержка для ожидания запуска процесса
                self.logger.info(f"{self.process_name} был запущен.")
            except Exception as e:
                self.logger.error(f"Ошибка при запуске процесса: {e}")
                raise  # Поднимаем исключение, чтобы остановить тест
        else:
            self.logger.info(f"{self.process_name} уже запущен. Процесс не будет запущен.")

    def kill_process(self):
        """Завершает процесс с заданным именем."""
        process = self.is_process_running()
        if process:
            try:
                process.terminate()  # Рассмотреть process.kill() для принудительного завершения
                process.wait()  # Ждем завершения процесса
                self.logger.info(f"Процесс '{self.process_name}' завершен.")
            except psutil.NoSuchProcess:
                self.logger.info("Процесс уже завершен.")
            except psutil.AccessDenied:
                self.logger.warning("Нет доступа для завершения процесса.")
            except Exception as e:
                self.logger.error(f"Ошибка при завершении процесса: {e}")
        else:
            self.logger.info(f"Процесс '{self.process_name}' не найден.")
