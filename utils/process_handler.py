import os
import subprocess
import time

import psutil
import win32con
import win32gui
import win32process

from utils.logger_config import setup_logger


class ProcessManager:
    _instance = None

    def __new__(cls, process_path, process_name, config_file_path=None):
        if cls._instance is None:
            cls._instance = super(ProcessManager, cls).__new__(cls)
            cls._instance.init(process_path, process_name, config_file_path)
        return cls._instance

    def init(self, process_path, process_name, config_file_path=None):
        self.process_path = process_path
        self.process_name = process_name
        self.config_file_path = config_file_path
        self.logger = setup_logger(self.process_name)

    def delete_config_file(self):
        """Удаляет конфигурационный файл перед запуском процесса."""
        if self.config_file_path and os.path.exists(self.config_file_path):
            try:
                os.remove(self.config_file_path)
                self.logger.info(f"Файл конфигурации {self.config_file_path} был удален.")
                return True
            except Exception as e:
                self.logger.error(f"Ошибка при удалении файла конфигурации: {e}")
                return False
        elif self.config_file_path:
            self.logger.info(f"Файл конфигурации {self.config_file_path} не существует.")
            return True
        else:
            self.logger.info("Путь к файлу конфигурации не указан.")
            return True

    def is_process_running(self):
        """Поддержка обратной совместимости: возвращает первый найденный процесс."""
        for proc in psutil.process_iter(attrs=['name']):
            if proc.info['name'] and proc.info['name'].lower() == self.process_name.lower():
                return proc
        return None

    def iter_processes(self):
        """Возвращает генератор по всем процессам с нужным именем."""
        for proc in psutil.process_iter(attrs=['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == self.process_name.lower():
                    yield proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def start_process(self):
        """Запускает процесс, предварительно закрывая его (если запущен) и удаляя конфигурационный файл."""
        # Сначала проверяем, запущен ли процесс, и если да - закрываем его
        process = self.is_process_running()
        if process:
            self.logger.info(f"{self.process_name} уже запущен. Завершаем процесс...")
            self.kill_process()

        # Затем удаляем конфигурационный файл
        if not self.delete_config_file():
            self.logger.warning("Не удалось удалить конфигурационный файл, но продолжим запуск процесса.")

        # Запускаем процесс
        try:
            process = subprocess.Popen(self.process_path)  # Запускаем процесс напрямую
            self.wait_for_process_ready(process.pid)
            self.logger.info(f"{self.process_name} был запущен.")
        except Exception as e:
            self.logger.error(f"Ошибка при запуске процесса: {e}")
            raise  # Поднимаем исключение, чтобы остановить тест

    def wait_for_process_ready(self, pid, timeout=20, poll_interval=0.1):
        """Wait until VT owns a visible window instead of sleeping a fixed 15 seconds."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            # VT uses a short-lived launcher process and creates its UI in a
            # second VT_Publisher process, so the Popen PID is not necessarily
            # the PID that owns the main window.
            for process in list(self.iter_processes()):
                try:
                    window_handle = self.get_window_handle(process.pid)
                    if window_handle and win32gui.IsWindowVisible(window_handle):
                        window_title = win32gui.GetWindowText(window_handle)
                        if "VT Publisher" in window_title:
                            return window_handle
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            time.sleep(poll_interval)

        raise TimeoutError(
            f"{self.process_name} (launcher PID {pid}) did not expose a responsive "
            f"window within {timeout} seconds."
        )

    def kill_process(self):
        """Завершает все инстансы процесса. Мягко (WM_CLOSE/terminate), затем форс-килл (taskkill)."""
        found_any = False
        try:
            # Сначала мягко закрываем все найденные процессы и их потомков
            for process in list(self.iter_processes()):
                found_any = True

                def terminate_process(proc):
                    try:
                        proc.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                def close_process(proc):
                    try:
                        hwnd = self.get_window_handle(proc.pid)
                        if hwnd:
                            try:
                                win32gui.PostMessage(
                                    hwnd,
                                    win32con.WM_CLOSE,
                                    0,
                                    0,
                                )
                            except Exception as error:
                                self.logger.warning(
                                    f"Could not send WM_CLOSE to "
                                    f"{self.process_name} PID {proc.pid}: "
                                    f"{error}. Falling back to terminate()."
                                )
                                terminate_process(proc)
                        else:
                            terminate_process(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                    except Exception as error:
                        self.logger.warning(
                            f"Could not close {self.process_name} PID "
                            f"{getattr(proc, 'pid', 'unknown')}: {error}. "
                            "Falling back to terminate()."
                        )
                        terminate_process(proc)

                try:
                    children = process.children(recursive=True)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    children = []

                for child in children:
                    close_process(child)
                close_process(process)

            # Ждем до 10 секунд, чтобы мягкое закрытие сработало
            deadline = time.time() + 10
            while time.time() < deadline:
                if not any(True for _ in self.iter_processes()):
                    break
                time.sleep(0.5)

            # Если что-то осталось — форс-киллим через taskkill
            if any(True for _ in self.iter_processes()):
                self.logger.info("Остались живые процессы, выполняем форс-килл через taskkill /F /T ...")
                try:
                    subprocess.run([
                        'taskkill', '/F', '/IM', self.process_name, '/T'
                    ], check=False, capture_output=True, text=True)
                except Exception as e:
                    self.logger.error(f"Ошибка при вызове taskkill: {e}")

                # Ждём до 5 секунд после форс-килла
                deadline_post = time.time() + 5
                while time.time() < deadline_post:
                    if not any(True for _ in self.iter_processes()):
                        break
                    time.sleep(0.5)

            if any(True for _ in self.iter_processes()):
                self.logger.warning(f"Некоторые процессы '{self.process_name}' все еще живы после форс-килла.")
            elif found_any:
                self.logger.info(f"Все инстансы процесса '{self.process_name}' завершены.")
            else:
                self.logger.info(f"Процесс '{self.process_name}' не найден.")
        except Exception as e:
            self.logger.error(f"Непредвиденная ошибка при завершении процесса: {e}")

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
