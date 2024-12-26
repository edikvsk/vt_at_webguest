import subprocess
import time

import psutil
import win32con
import win32gui
import win32process

from utils.logger_config import setup_logger


class ProcessManager:
    _instance = None

    def __new__(cls, process_path, process_name):
        if cls._instance is None:
            cls._instance = super(ProcessManager, cls).__new__(cls)
            cls._instance.init(process_path, process_name)
        return cls._instance

    def init(self, process_path, process_name):
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
        """Завершает дерево процессов с заданным именем."""
        process = self.is_process_running()
        if process:
            try:
                # Функция для отправки сообщения WM_CLOSE
                def close_process(proc):
                    hwnd = self.get_window_handle(proc.pid)
                    if hwnd:
                        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    else:
                        proc.terminate()  # Если окна нет, принудительно завершаем

                # Попытка закрыть дочерние процессы
                for child in process.children(recursive=True):
                    close_process(child)

                # Попытка закрыть основной процесс
                close_process(process)

                process.wait()  # Ждем завершения процесса
                self.logger.info(f"Процесс '{self.process_name}' и его дочерние процессы завершены.")
            except psutil.NoSuchProcess:
                self.logger.info("Процесс уже завершен.")
            except psutil.AccessDenied:
                self.logger.warning("Нет доступа для завершения процесса.")
            except Exception as e:
                self.logger.error(f"Ошибка при завершении процесса: {e}")
        else:
            self.logger.info(f"Процесс '{self.process_name}' не найден.")

    def get_window_handle(self, pid):
        """Возвращает дескриптор окна для процесса по его PID."""

        def enum_windows(hwnd, pid):
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    handles.append(hwnd)

        handles = []
        win32gui.EnumWindows(enum_windows, pid)
        return handles[0] if handles else None
