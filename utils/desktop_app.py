import os

from pywinauto import Application
from pywinauto.application import AppStartError

import os
import shutil

from utils.config import PROCESS_PATH, CONFIG_INI


class DesktopApp:
    def __init__(self, app_path=None, cleanup_paths=None):
        self.app_path = app_path or PROCESS_PATH
        self.app = None
        self.main_window = None
        self.cleanup_paths = cleanup_paths or self.get_default_cleanup_paths()

        # Очистка файлов перед запуском
        self.cleanup_local_files()
        self.start_application()

    def get_default_cleanup_paths(self):
        """Возвращает пути по умолчанию для очистки"""
        vt_directory = os.path.dirname(PROCESS_PATH)
        return [
            os.path.join(vt_directory, "DLL", "publisher.xml"),
            os.path.join(vt_directory, "DLL", "receiver.xml"),
            CONFIG_INI
        ]

    def cleanup_local_files(self):
        """Удаляет локальные файлы и директории перед запуском приложения"""
        if not self.cleanup_paths:
            print("Нет файлов для очистки.")
            return

        print("Начинается очистка локальных файлов...")
        for file_path in self.cleanup_paths:
            try:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"✓ Удален файл: {file_path}")
                    else:
                        shutil.rmtree(file_path)
                        print(f"✓ Удалена директория: {file_path}")
                else:
                    print(f"⚠ Файл не существует: {file_path}")
            except PermissionError:
                print(f"❌ Ошибка доступа: {file_path} (файл используется другим процессом)")
            except Exception as e:
                print(f"❌ Ошибка при удалении {file_path}: {e}")
        print("Очистка завершена.")

    def start_application(self):
        if not os.path.exists(self.app_path):
            raise FileNotFoundError(f"Приложение не найдено по пути: {self.app_path}")

        try:
            # Попытка подключиться к уже запущенному приложению
            self.app = Application(backend='uia').connect(path=self.app_path)
            print("Приложение успешно подключено.")
        except AppStartError:
            print("Приложение не запущено. Попытка запуска...")
            # Если приложение не запущено, запускаем его
            self.app = Application(backend='uia').start(self.app_path)
            print("Приложение запущено.")

        # Получаем главное окно приложения
        self.main_window = self.app.window(title_re="VT Publisher.*")
        self.activate_window()

    def activate_window(self):
        if self.main_window.exists():
            self.main_window.set_focus()
            print("Главное окно приложения активировано.")
        else:
            raise Exception("Главное окно приложения не найдено.")

    def close_application(self):
        if self.app is not None:
            self.app.kill()  # Завершение процесса приложения
            print("Приложение закрыто.")