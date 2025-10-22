"""
Улучшенная система управления конфигурацией с поддержкой переменных окружения,
валидации и различных источников конфигурации.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union, Tuple
import re
import zipfile
import urllib.request
import shutil
from dataclasses import dataclass, field
from .device_manager import device_manager


@dataclass
class BrowserConfig:
    """Конфигурация браузера."""
    chrome_driver_path: str
    chrome_browser_path: str
    window_width: int = 1920
    window_height: int = 1080
    headless: bool = False
    additional_options: list = field(default_factory=list)


@dataclass
class DesktopAppConfig:
    """Конфигурация десктопного приложения."""
    process_path: str
    process_name: str
    publisher_xml_path: str
    config_ini_path: str
    source_to_publishing: str


@dataclass
class MediaDevicesConfig:
    """Конфигурация медиа-устройств."""
    video_device_id: str
    audio_device_id: str
    camera_for_selection: str
    mic_for_selection: str


@dataclass
class TestConfig:
    """Общие настройки тестов."""
    default_timeout: int = 10
    long_timeout: int = 30
    short_timeout: int = 5
    retry_count: int = 3
    retry_delay: float = 1.0
    screenshot_on_failure: bool = True
    video_recording: bool = False


class ConfigManager:
    """Менеджер конфигурации с поддержкой различных источников."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_file = config_file
        self._browser_config: Optional[BrowserConfig] = None
        self._desktop_config: Optional[DesktopAppConfig] = None
        self._media_config: Optional[MediaDevicesConfig] = None
        self._test_config: Optional[TestConfig] = None
        
        # Загружаем конфигурацию при инициализации
        self._load_config()

    def _repo_root(self) -> Path:
        """Возвращает корень репозитория (папка с utils/ на один уровень выше)."""
        return Path(__file__).resolve().parent.parent

    def _detect_browser_paths_from_tools(self) -> Dict[str, Optional[str]]:
        """Пытается найти Chrome/Chromedriver в локальном каталоге .tools.
        Возвращает словарь с ключами chrome_path, driver_path (или None).
        """
        tools_dir = self._repo_root() / ".tools"
        chrome_path: Optional[str] = None
        driver_path: Optional[str] = None
        try:
            if tools_dir.exists():
                # Ищем Chrome for Testing
                chrome_candidates = list(tools_dir.glob("chrome-*/chrome-win64/chrome.exe"))
                if chrome_candidates:
                    # Берем наиболее свежий по времени изменения
                    chrome_candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                    chrome_path = str(chrome_candidates[0])
                # Ищем Chromedriver
                driver_candidates = list(tools_dir.glob("chromedriver-*/chromedriver-win64/chromedriver.exe"))
                if driver_candidates:
                    driver_candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                    driver_path = str(driver_candidates[0])
        except Exception as e:
            self.logger.debug(f"Автопоиск в .tools завершился с ошибкой: {e}")
        return {"chrome_path": chrome_path, "driver_path": driver_path}

    def _vt_cache_dir(self) -> Path:
        """Локальный кэш для VT сборок."""
        return self._repo_root() / ".tools" / "VT"

    def _fetch_url_text(self, url: str) -> str:
        """Скачивает содержимое URL как текст (utf-8)."""
        with urllib.request.urlopen(url) as resp:
            return resp.read().decode("utf-8", errors="ignore")

    def _detect_latest_vt_version(self) -> Optional[str]:
        """Определяет последнюю доступную версию VT с индексной страницы.

        Ожидается формат подкаталогов вида 1.9.5.1199/
        """
        try:
            index_html = self._fetch_url_text("http://releases.medialooks.net/VT/")
        except Exception as e:
            self.logger.warning(f"Не удалось получить список сборок VT: {e}")
            return None

        # Ищем ссылки на подкаталоги версий
        # Пример: <a href="1.9.5.1199/">1.9.5.1199/</a>
        versions = re.findall(r"href=\"(\d+\.\d+\.\d+\.\d+)/\"", index_html)
        if not versions:
            return None

        def version_key(v: str) -> Tuple[int, int, int, int]:
            try:
                return tuple(int(x) for x in v.split("."))  # type: ignore[return-value]
            except Exception:
                return (0, 0, 0, 0)

        versions.sort(key=version_key, reverse=True)
        return versions[0]

    def _ensure_latest_vt_downloaded(self) -> Optional[Path]:
        """Гарантирует наличие распакованной последней dev.dev.x64 сборки.

        Возвращает путь к корневой папке вида "Video Transport <ver>(x64)",
        либо None при неудаче.
        """
        latest = self._detect_latest_vt_version()
        if not latest:
            return None

        cache_dir = self._vt_cache_dir() / latest
        target_dir_glob = list(cache_dir.glob("Video Transport * (x64)"))
        # Некоторые индексы содержат формат без пробела: "Video Transport 1.9.5.1199(x64)"
        if not target_dir_glob:
            target_dir_glob = list(cache_dir.glob("Video Transport *(x64)"))

        if target_dir_glob:
            return target_dir_glob[0]

        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            zip_name = f"Video Transport {latest}.dev.dev.x64.zip"
            zip_url = f"http://releases.medialooks.net/VT/{latest}/{urllib.parse.quote(zip_name)}"
            zip_path = cache_dir / zip_name

            if not zip_path.exists():
                self.logger.info(f"Скачиваю VT сборку: {zip_url}")
                urllib.request.urlretrieve(zip_url, str(zip_path))

            self.logger.info("Распаковываю архив VT...")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(cache_dir)

            target_dir_glob = list(cache_dir.glob("Video Transport * (x64)"))
            if not target_dir_glob:
                target_dir_glob = list(cache_dir.glob("Video Transport *(x64)"))

            return target_dir_glob[0] if target_dir_glob else None
        except Exception as e:
            self.logger.warning(f"Не удалось скачать/распаковать VT {latest}: {e}")
            return None
    
    def _get_env_or_default(self, env_var: str, default: Any, var_type: type = str) -> Any:
        """
        Получает значение из переменной окружения или возвращает значение по умолчанию.
        
        Args:
            env_var: Имя переменной окружения
            default: Значение по умолчанию
            var_type: Тип переменной для преобразования
            
        Returns:
            Значение из окружения или по умолчанию
        """
        value = os.getenv(env_var)
        if value is None:
            return default
            
        try:
            if var_type == bool:
                return value.lower() in ('true', '1', 'yes', 'on')
            elif var_type == int:
                return int(value)
            elif var_type == float:
                return float(value)
            else:
                return str(value)
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Ошибка преобразования переменной окружения {env_var}: {e}. Используется значение по умолчанию.")
            return default
    
    def _validate_path(self, path: str, description: str) -> bool:
        """
        Валидирует существование пути.
        
        Args:
            path: Путь для проверки
            description: Описание пути для логирования
            
        Returns:
            True если путь существует, False иначе
        """
        if not path:
            self.logger.error(f"{description}: путь не указан")
            return False
            
        path_obj = Path(path)
        if not path_obj.exists():
            self.logger.error(f"{description}: путь не существует - {path}")
            return False
            
        self.logger.debug(f"{description}: путь валиден - {path}")
        return True
    
    def _load_config(self) -> None:
        """Загружает конфигурацию из различных источников."""
        try:
            # Автопоиск путей к браузеру/драйверу из .tools, если переменные окружения не заданы
            detected = self._detect_browser_paths_from_tools()

            # Загружаем конфигурацию браузера
            self._browser_config = BrowserConfig(
                chrome_driver_path=self._get_env_or_default(
                    'CHROME_DRIVER_PATH', 
                    detected.get('driver_path') or "D:/chromedriver/chromedriver.exe"
                ),
                chrome_browser_path=self._get_env_or_default(
                    'CHROME_BROWSER_PATH',
                    detected.get('chrome_path') or "C:/Program Files/Google/Chrome/Application/chrome.exe"
                ),
                window_width=self._get_env_or_default('BROWSER_WINDOW_WIDTH', 1920, int),
                window_height=self._get_env_or_default('BROWSER_WINDOW_HEIGHT', 1080, int),
                headless=self._get_env_or_default('BROWSER_HEADLESS', False, bool)
            )
            
            # Пытаемся автоматически подготовить пути VT, если env не заданы
            env_process_path = os.getenv('VT_PROCESS_PATH')
            env_xml_path = os.getenv('VT_PUBLISHER_XML_PATH')

            auto_root = None
            if not env_process_path or not env_xml_path:
                auto_root = self._ensure_latest_vt_downloaded()

            if auto_root is not None:
                default_process = str(auto_root / "VT_Publisher.exe")
                default_xml = str(auto_root / "DLL" / "publisher.xml")
            else:
                # fallback на прежние дефолты, если автозагрузка не удалась
                default_process = "C:/Users/edwar/Desktop/VT/Video Transport 1.9.5.1179(x64)/VT_Publisher.exe"
                default_xml = "C:/Users/edwar/Desktop/VT/Video Transport 1.9.5.1179(x64)/DLL/publisher.xml"

            # Загружаем конфигурацию десктопного приложения
            self._desktop_config = DesktopAppConfig(
                process_path=self._get_env_or_default('VT_PROCESS_PATH', default_process),
                process_name=self._get_env_or_default('VT_PROCESS_NAME', "VT_Publisher.exe"),
                publisher_xml_path=self._get_env_or_default('VT_PUBLISHER_XML_PATH', default_xml),
                config_ini_path=self._get_env_or_default(
                    'VT_CONFIG_INI_PATH',
                    str(self._repo_root() / "utils" / "config.ini")
                ),
                source_to_publishing=self._get_env_or_default('VT_SOURCE_TO_PUBLISHING', "Screen:")
            )

            # Копируем private.json рядом с VT_Publisher.exe, если указано
            try:
                private_json_src = self._get_env_or_default(
                    'VT_PRIVATE_JSON_PATH',
                    r"\\192.168.10.100\MLFiles\Trash\EdikV_tester\auto@test.ru_vt08.medialooks.com.private.json"
                )
                if private_json_src:
                    # Нормализуем UNC: приводим к виду \\server\share\...
                    if private_json_src.startswith('\\\\\\\\'):
                        # Сжимаем четыре начальных слеша до двух
                        private_json_src = '\\\\' + private_json_src.lstrip('\\')
                    elif private_json_src.startswith('\\\\'):
                        # уже корректный UNC
                        pass
                    elif private_json_src.startswith('\\'):
                        # одиночная обратная черта в начале → сделаем UNC
                        private_json_src = '\\' + private_json_src

                    proc_dir = Path(self._desktop_config.process_path).parent
                    src_path = Path(private_json_src)
                    dst_path = proc_dir / src_path.name
                    # Пытаемся скопировать, перезаписываем при необходимости
                    if src_path.exists():
                        shutil.copy2(str(src_path), str(dst_path))
                        self.logger.info(f"Скопирован private.json в: {dst_path}")
                    else:
                        self.logger.warning(f"Файл private.json не найден по пути: {private_json_src}")
            except Exception as copy_err:
                self.logger.warning(f"Не удалось скопировать private.json: {copy_err}")
            
            # Загружаем конфигурацию медиа-устройств с автоматическим определением ID
            self._media_config = self._load_media_devices_config()
            
            # Загружаем конфигурацию тестов
            self._test_config = TestConfig(
                default_timeout=self._get_env_or_default('TEST_DEFAULT_TIMEOUT', 10, int),
                long_timeout=self._get_env_or_default('TEST_LONG_TIMEOUT', 30, int),
                short_timeout=self._get_env_or_default('TEST_SHORT_TIMEOUT', 5, int),
                retry_count=self._get_env_or_default('TEST_RETRY_COUNT', 3, int),
                retry_delay=self._get_env_or_default('TEST_RETRY_DELAY', 1.0, float),
                screenshot_on_failure=self._get_env_or_default('TEST_SCREENSHOT_ON_FAILURE', True, bool),
                video_recording=self._get_env_or_default('TEST_VIDEO_RECORDING', False, bool)
            )
            
            self.logger.info("Конфигурация успешно загружена")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")
            raise
    
    def validate_config(self) -> bool:
        """
        Валидирует всю конфигурацию.
        
        Returns:
            True если конфигурация валидна, False иначе
        """
        is_valid = True
        
        # Валидация браузера
        if not self._validate_path(self.browser.chrome_driver_path, "Chrome Driver"):
            is_valid = False
        if not self._validate_path(self.browser.chrome_browser_path, "Chrome Browser"):
            is_valid = False
            
        # Валидация десктопного приложения
        if not self._validate_path(self.desktop.process_path, "VT Process"):
            is_valid = False
        if not self._validate_path(
            os.path.dirname(self.desktop.publisher_xml_path), 
            "Publisher XML Directory"
        ):
            is_valid = False
            
        # Валидация медиа-устройств
        if not self.media.video_device_id:
            self.logger.error("Video Device ID не указан")
            is_valid = False
        if not self.media.audio_device_id:
            self.logger.error("Audio Device ID не указан")
            is_valid = False
            
        # Валидация настроек тестов
        if self.test.default_timeout <= 0:
            self.logger.error("Default timeout должен быть больше 0")
            is_valid = False
        if self.test.retry_count < 0:
            self.logger.error("Retry count не может быть отрицательным")
            is_valid = False
            
        if is_valid:
            self.logger.info("Конфигурация прошла валидацию")
        else:
            self.logger.error("Конфигурация содержит ошибки")
        return is_valid
            
    def _load_media_devices_config(self) -> MediaDevicesConfig:
        """
        Загружает конфигурацию медиа-устройств с автоматическим определением ID.
        
        Returns:
            Объект MediaDevicesConfig
        """
        # Получаем имена устройств из переменных окружения
        camera_name = self._get_env_or_default('CAMERA_FOR_SELECTION', "Logi")
        mic_name = self._get_env_or_default('MIC_FOR_SELECTION', "Logi")
        
        # Пытаемся найти устройства по имени
        video_device_id = None
        audio_device_id = None
        
        try:
            # Ищем видеоустройство
            video_device = device_manager.find_video_device_by_name(camera_name)
            if video_device:
                video_device_id = video_device.device_id
                self.logger.info(f"Найдено видеоустройство: {video_device.label}")
            else:
                self.logger.warning(f"Видеоустройство с именем '{camera_name}' не найдено")
            
            # Ищем аудиоустройство
            audio_device = device_manager.find_audio_device_by_name(mic_name)
            if audio_device:
                audio_device_id = audio_device.device_id
                self.logger.info(f"Найдено аудиоустройство: {audio_device.label}")
            else:
                self.logger.warning(f"Аудиоустройство с именем '{mic_name}' не найдено")
                
        except Exception as e:
            self.logger.error(f"Ошибка при поиске устройств: {e}")
        
        # Используем найденные ID или значения по умолчанию
        return MediaDevicesConfig(
            video_device_id=self._get_env_or_default(
                'VIDEO_DEVICE_ID',
                video_device_id or "85c5169a41b10634c11c439fb883f3b990ad69b6082dbabedea6635e12c61591"
            ),
            audio_device_id=self._get_env_or_default(
                'AUDIO_DEVICE_ID',
                audio_device_id or "7fd76655b10bf621fbeb2a96c3021f33c5c325b9b4fff386263f9d59556f5c6a"
            ),
            camera_for_selection=camera_name,
            mic_for_selection=mic_name
        )
    
    @property
    def browser(self) -> BrowserConfig:
        """Возвращает конфигурацию браузера."""
        return self._browser_config
    
    @property
    def desktop(self) -> DesktopAppConfig:
        """Возвращает конфигурацию десктопного приложения."""
        return self._desktop_config
    
    @property
    def media(self) -> MediaDevicesConfig:
        """Возвращает конфигурацию медиа-устройств."""
        return self._media_config
    
    @property
    def test(self) -> TestConfig:
        """Возвращает конфигурацию тестов."""
        return self._test_config
    
    def get_chrome_options(self) -> list:
        """
        Возвращает список опций для Chrome.
        
        Returns:
            Список опций Chrome
        """
        options = [
            "--use-fake-ui-for-media-stream",
            "--enable-gpu",
            "--disable-software-rasterizer",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            # Минимизация WebRTC ошибок
            "--disable-logging",
            "--log-level=3",  # Только критические ошибки
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-features=TranslateUI,BlinkGenPropertyTrees",
            "--disable-ipc-flooding-protection",
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-sync",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-translate",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--silent",
            "--disable-gpu-logging"
        ]
        
        if self.browser.headless:
            options.append("--headless")
            
        # Добавляем дополнительные опции если есть
        options.extend(self.browser.additional_options)
        
        # Добавляем опции для работы с реальными медиа-устройствами
        if self.media.video_device_id:
            options.append("--use-fake-ui-for-media-stream")  # Убираем запрос разрешений
            options.append("--enable-experimental-web-platform-features")
            options.append("--disable-features=VizDisplayCompositor")
            options.append("--autoplay-policy=no-user-gesture-required")
            options.append("--disable-web-security")
            options.append("--allow-running-insecure-content")
            options.append("--disable-features=TranslateUI")
            options.append("--disable-ipc-flooding-protection")
            # Разрешаем доступ к реальным устройствам
            options.append("--enable-media-stream")
            options.append("--allow-file-access-from-files")
        
        return options
    
    def print_config_summary(self) -> None:
        """Выводит сводку конфигурации."""
        print("\n" + "="*50)
        print("СВОДКА КОНФИГУРАЦИИ")
        print("="*50)
        
        print(f"\n📁 ПУТИ:")
        print(f"  Chrome Driver: {self.browser.chrome_driver_path}")
        print(f"  Chrome Browser: {self.browser.chrome_browser_path}")
        print(f"  VT Process: {self.desktop.process_path}")
        print(f"  Config INI: {self.desktop.config_ini_path}")
        
        print(f"\n🎥 МЕДИА-УСТРОЙСТВА:")
        print(f"  Video Device ID: {self.media.video_device_id[:20]}...")
        print(f"  Audio Device ID: {self.media.audio_device_id[:20]}...")
        print(f"  Camera: {self.media.camera_for_selection}")
        print(f"  Microphone: {self.media.mic_for_selection}")
        
        print(f"\n⚙️ НАСТРОЙКИ ТЕСТОВ:")
        print(f"  Default Timeout: {self.test.default_timeout}с")
        print(f"  Long Timeout: {self.test.long_timeout}с")
        print(f"  Retry Count: {self.test.retry_count}")
        print(f"  Screenshots: {'Включены' if self.test.screenshot_on_failure else 'Отключены'}")
        
        print(f"\n🌐 БРАУЗЕР:")
        print(f"  Размер окна: {self.browser.window_width}x{self.browser.window_height}")
        print(f"  Headless: {'Включен' if self.browser.headless else 'Отключен'}")
        
        print("="*50 + "\n")


# Глобальный экземпляр конфигурации
config = ConfigManager()

# Экспортируем для обратной совместимости
CHROME_DRIVER_PATH = config.browser.chrome_driver_path
CHROME_BROWSER_PATH = config.browser.chrome_browser_path
PROCESS_PATH = config.desktop.process_path
PROCESS_NAME = config.desktop.process_name
PUBLISHER_XML_PATH = config.desktop.publisher_xml_path
CONFIG_INI = config.desktop.config_ini_path
SOURCE_TO_PUBLISHING = config.desktop.source_to_publishing
VIDEO_DEVICE_ID = config.media.video_device_id
AUDIO_DEVICE_ID = config.media.audio_device_id
CAMERA_FOR_SELECTION_IN_TEST_CAMERA_SELECT = config.media.camera_for_selection
MIC_FOR_SELECTION_IN_TEST_MICROPHONE_SELECT = config.media.mic_for_selection
