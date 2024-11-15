import os

from pywinauto import Application
from pywinauto.application import AppStartError


class DesktopApp:
    def __init__(self, app_path):
        self.app_path = app_path
        self.app = None
        self.main_window = None
        self.start_application()

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
