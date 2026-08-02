import configparser
import logging
from typing import Optional
import os
import glob
import time
from datetime import datetime
from urllib.parse import urlparse

import pyperclip
import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.config import (CHROME_DRIVER_PATH, CHROME_BROWSER_PATH, PROCESS_PATH, PROCESS_NAME, SOURCE_TO_PUBLISHING,
                          VIDEO_DEVICE_ID, AUDIO_DEVICE_ID, CONFIG_INI, PUBLISHER_XML_PATH)
from utils.config_manager import config
from utils.desktop_app import DesktopApp
from utils.notificaton_handler import NotificationHandler
from utils.process_handler import ProcessManager
from utils.webrtc_stream_handler import StreamHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True, scope="function")
def ensure_vt_killed_before_test():
    """Гарантированно закрывает VT перед каждым тестом, чтобы избежать зависаний на открытой вкладке."""
    pm = ProcessManager(PROCESS_PATH, PROCESS_NAME, PUBLISHER_XML_PATH)
    pm.kill_process()
    # небольшая пауза, чтобы ОС пересобрала дескрипторы окон
    import time as _t
    _t.sleep(1)
    try:
        yield
    finally:
        pm.kill_process()


@pytest.fixture(scope="function")
def driver(ensure_vt_killed_before_test, request):
    """Основная фикстура для создания WebDriver с настройкой браузера и запуском процесса."""
    # Подавляем WebRTC логи
    import os
    os.environ['WEBRTC_LOGGING'] = '0'
    os.environ['WEBRTC_DEBUG'] = '0'
    
    process_manager = ProcessManager(PROCESS_PATH, PROCESS_NAME, PUBLISHER_XML_PATH)
    process_manager.start_process()

    chrome_options = Options()
    
    # Получаем опции Chrome из конфигурационного менеджера
    chrome_options_list = config.get_chrome_options()
    for option in chrome_options_list:
        chrome_options.add_argument(option)
    
    chrome_options.binary_location = CHROME_BROWSER_PATH

    # Добавляем медиа-ограничения через экспериментальные опции
    media_constraints = {
        "video": {"deviceId": {"exact": VIDEO_DEVICE_ID}},
        "audio": {"deviceId": {"exact": AUDIO_DEVICE_ID}}
    }
    
    # Устанавливаем медиа-ограничения через экспериментальные опции
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.notifications": 1
    })
    
    # Добавляем медиа-ограничения через экспериментальные опции
    chrome_options.add_experimental_option("useAutomationExtension", False)
    # Убираем лишние логи Chrome/ChromeDriver в консоль
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])  # скрыть драйвер-логи
    chrome_options.add_argument("--log-level=3")  # минимизировать уровень логов Chrome

    # Глушим лог-файл chromedriver
    service = Service(CHROME_DRIVER_PATH, log_path=os.devnull)
    web_driver = webdriver.Chrome(service=service, options=chrome_options)
    # Register cleanup immediately so setup failures cannot leak Chrome.
    request.addfinalizer(web_driver.quit)
    
    # Максимизируем окно для более стабильной работы
    web_driver.maximize_window()
    
    # Устанавливаем медиа-ограничения через JavaScript после загрузки страницы
    web_driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': f'''
            // Переопределяем getUserMedia для автоматического выбора устройств
            const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
            navigator.mediaDevices.getUserMedia = function(constraints) {{
                console.log('Original constraints:', constraints);
                
                // Сначала получаем список доступных устройств
                return navigator.mediaDevices.enumerateDevices().then(devices => {{
                    console.log('Available devices:', devices);
                    
                    // Ищем устройства по имени (частичное совпадение)
                    const cameraName = "{config.media.camera_for_selection}";
                    const micName = "{config.media.mic_for_selection}";
                    
                    let videoDeviceId = null;
                    let audioDeviceId = null;
                    
                    // Ищем видеоустройство
                    const videoDevices = devices.filter(d => d.kind === 'videoinput');
                    for (const device of videoDevices) {{
                        if (device.label.toLowerCase().includes(cameraName.toLowerCase())) {{
                            videoDeviceId = device.deviceId;
                            console.log('Found video device:', device.label, 'ID:', device.deviceId);
                            break;
                        }}
                    }}
                    
                    // Ищем аудиоустройство
                    const audioDevices = devices.filter(d => d.kind === 'audioinput');
                    for (const device of audioDevices) {{
                        if (device.label.toLowerCase().includes(micName.toLowerCase())) {{
                            audioDeviceId = device.deviceId;
                            console.log('Found audio device:', device.label, 'ID:', device.deviceId);
                            break;
                        }}
                    }}
                    
                    // Формируем constraints с найденными устройствами
                    const modifiedConstraints = {{}};

                    if (constraints.video !== false) {{
                        if (videoDeviceId) {{
                            modifiedConstraints.video = {{ ...constraints.video, deviceId: {{ exact: videoDeviceId }} }};
                        }} else {{
                            modifiedConstraints.video = true;
                        }}
                    }}

                    if (constraints.audio !== false) {{
                        if (audioDeviceId) {{
                            modifiedConstraints.audio = {{ ...constraints.audio, deviceId: {{ exact: audioDeviceId }} }};
                        }} else {{
                            modifiedConstraints.audio = true;
                        }}
                    }}
                    
                    console.log('Modified constraints:', modifiedConstraints);
                    return originalGetUserMedia.call(this, modifiedConstraints);
                }});
            }};
        '''
    })
    
    return web_driver


@pytest.fixture(scope="function")
def desktop_app_setup():
    """Фикстура для настройки десктопного приложения."""
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)
    return desktop_app, desktop_app_page


@pytest.fixture(scope="function")
def web_guest_page_setup(driver):
    """Фикстура для настройки веб-страницы гостя."""
    web_guest_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    notification_handler = NotificationHandler(driver, web_guest_page.NOTIFICATION_ELEMENT, logger)
    stream_handler = StreamHandler(driver)
    return web_guest_page, base_page, notification_handler, stream_handler


def _valid_copied_url(value: Optional[str], copy_command: str = "") -> Optional[str]:
    """Return a normalized copied URL only when it is a real HTTP endpoint."""
    if not value:
        return None
    url = value.strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    if "Web Guest" in copy_command and "/wg" not in parsed.path.casefold():
        return None
    return url


def get_web_url(desktop_app_page: DesktopAppPage, logger: logging.Logger, copy_command: str) -> Optional[str]:
    """
    Упрощённый и быстрый способ получить URL из десктопного приложения.

    Всегда выполняет только "Start Publishing" (без логики переключения) и копирует URL
    через контекстное меню. Используется там, где требуется именно путь через UI.
    """
    try:
        desktop_app_page.focus_click_vt_source_item(SOURCE_TO_PUBLISHING)

        # Всегда пытаемся нажать только Start Publishing (приложение запускается с нуля)
        if desktop_app_page.check_element_enabled_by_title_part("Start Publishing"):
            desktop_app_page.click_button_by_name("Start Publishing")
            time.sleep(1)

        # Clear the clipboard so a failed menu click cannot reuse a URL from a
        # previous test. Publisher may need a moment to create its room URL.
        clipboard_marker = f"VT_URL_PENDING_{time.time_ns()}"
        pyperclip.copy(clipboard_marker)

        last_error = None
        for attempt in range(1, 6):
            try:
                desktop_app_page.right_click_vt_source_item(SOURCE_TO_PUBLISHING)
                time.sleep(0.4)
                desktop_app_page.click_vt_source_item(copy_command)
            except Exception as exc:
                last_error = exc
                time.sleep(0.6)
                continue

            deadline = time.time() + 2
            while time.time() < deadline:
                copied = pyperclip.paste()
                url = _valid_copied_url(copied, copy_command)
                if url:
                    logger.info(f"Получен URL: {url}")
                    return url
                time.sleep(0.2)

            last_error = RuntimeError(
                f"Publisher did not copy a valid URL for '{copy_command}' "
                f"(clipboard={pyperclip.paste()!r}, attempt={attempt})."
            )

        raise last_error or RuntimeError(f"Could not copy URL using '{copy_command}'.")
    except Exception as e:
        logger.error(f"Ошибка при получении URL: {e}")
        return None


def _read_web_guest_url_from_config(config_path: str) -> Optional[str]:
    """Быстро читает web_guest_page_url из utils/config.ini (без UI)."""
    try:
        parser = configparser.ConfigParser()
        parser.read(config_path, encoding="utf-8")
        url = parser.get("DEFAULT", "web_guest_page_url", fallback=None)
        return _valid_copied_url(url, "Copy Web Guest URL")
    except Exception:
        return None


def update_config(config_file_path: str, section: str, key: str, value: str) -> bool:
    """
    Обновляет значение в конфигурационном файле.
    
    Args:
        config_file_path: Путь к файлу конфигурации
        section: Секция конфигурации
        key: Ключ
        value: Значение
        
    Returns:
        True если успешно, False в случае ошибки
    """
    try:
        config = configparser.ConfigParser()
        config.read(config_file_path)
        
        # Создаем секцию если её нет
        if section not in config:
            config.add_section(section)
            
        config[section][key] = value
        
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
        logger.info(f"Конфигурация обновлена: {section}.{key} = {value}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении конфигурации: {e}")
        return False


@pytest.fixture(scope="function")
def login_fixture(driver, logger):
    """Фикстура для авторизации на веб-странице гостя.

    Оптимизации:
    - Только запуск публикации (Start Publishing) без логики переключения.
    - Ссылку получаем через быстрый UI-путь копирования (актуальные динамические URL).
    """
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    web_guest_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    notification_handler = NotificationHandler(driver, web_guest_page.NOTIFICATION_ELEMENT, logger)
    stream_handler = StreamHandler(driver)

    try:
        # 1) Получаем актуальный URL через копирование из UI
        web_guest_url = get_web_url(desktop_app_page, logger, "Copy Web Guest URL")
        if not web_guest_url:
            logger.error("Не удалось получить Web Guest URL через UI.")
            raise ValueError("Web Guest URL не был инициализирован.")

        logger.info("Переходим на страницу Web Guest")
        driver.get(web_guest_url)

        notification_handler.check_notification()
        base_page.click(web_guest_page.LOGIN_BUTTON)
        stream_handler.wait_for_webrtc_connection(timeout=20)
        logger.info("Стрим запущен")

        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")
        raise


@pytest.fixture(scope="function")
def modified_fixture(driver, logger):
    """Фикстура для модифицированной настройки с сохранением URL в конфигурацию."""
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)
    web_guest_page = WebGuestPage(driver)

    try:
        web_guest_url = get_web_url(desktop_app_page, logger, "Copy Web Guest URL")
        if not web_guest_url:
            logger.warning("Не удалось получить URL через UI, читаем из конфига...")
            web_guest_url = _read_web_guest_url_from_config(CONFIG_INI)
        if not web_guest_url:
            logger.error("Не удалось получить Web Guest URL.")
            raise ValueError("Web Guest URL не был инициализирован.")

        update_config(CONFIG_INI, 'DEFAULT', 'WEB_GUEST_PAGE_URL', web_guest_url)
        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")
        raise


@pytest.fixture(scope="function")
def web_preview_fixture(driver, logger):
    """Фикстура для настройки веб-превью."""
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)
    web_guest_page = WebGuestPage(driver)

    try:
        web_preview_url = get_web_url(desktop_app_page, logger, "Copy Preview URL")
        if not web_preview_url:
            logger.error("Не удалось получить Preview URL.")
            raise ValueError("Preview URL не был инициализирован.")

        update_config(CONFIG_INI, 'DEFAULT', 'WEB_PREVIEW_PAGE_URL', web_preview_url)
        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")
        raise


@pytest.fixture(scope="function")
def open_web_preview_fixture(driver, logger):
    """Фикстура для открытия веб-превью (ускорённая).

    - Только один клик "Start Publishing" (если доступен).
    - Копируем Preview URL через UI и открываем напрямую в `driver` (не через меню "Open Preview URL").
    """
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)
    web_guest_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    notification_handler = NotificationHandler(driver, web_guest_page.NOTIFICATION_ELEMENT, logger)

    try:
        desktop_app_page.focus_click_vt_source_item(SOURCE_TO_PUBLISHING)
        if desktop_app_page.check_element_enabled_by_title_part("Start Publishing"):
            desktop_app_page.click_button_by_name("Start Publishing")

        preview_url = get_web_url(desktop_app_page, logger, "Copy Preview URL")
        if not preview_url:
            logger.error("Не удалось получить Preview URL через UI.")
            raise ValueError("Preview URL не был инициализирован.")

        logger.info("Переходим на страницу Web Preview")
        driver.get(preview_url)
        notification_handler.check_notification()
        base_page.click(web_guest_page.LOGIN_BUTTON)

        yield web_guest_page
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Ошибка при переходе на страницу: {e}")
        raise


@pytest.fixture(scope="function")
def test_logger():
    """Фикстура для создания логгера для конкретного теста."""
    import os
    import inspect
    
    # Получаем имя тестового файла
    frame = inspect.currentframe()
    test_file = None
    while frame:
        if 'test_' in frame.f_code.co_filename:
            test_file = frame.f_code.co_filename
            break
        frame = frame.f_back
    
    if test_file:
        test_name = os.path.splitext(os.path.basename(test_file))[0]
    else:
        test_name = "unknown_test"
    
    from utils.logger_config import setup_logger
    return setup_logger(test_name)


# -----------------------
# Pytest summary-репортинг
# -----------------------

def _find_latest_test_log_file(test_file_base: str) -> Optional[str]:
    """Ищет последний (по времени) лог-файл для указанного тестового файла.

    Логи создаются как logs/<test_file_base>_<timestamp>.log
    """
    pattern = os.path.join("logs", f"{test_file_base}_*.log")
    candidates = glob.glob(pattern)
    if not candidates:
        return None
    candidates.sort(key=lambda p: os.path.getmtime(p))
    return candidates[-1]


def _extract_last_step_or_error_from_log(log_path: str) -> Optional[str]:
    """Возвращает последнюю строку шага/ошибки из лог-файла.

    Ищем снизу строки, содержащие ключи шагов/ошибок.
    """
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        # Ищем с конца наиболее информативную строку
        keys = ("test_step", "шаг", " - ERROR - ", "✗", "ERROR")
        for line in reversed(lines):
            low = line.lower()
            if any(k in low for k in ("test_step", "шаг")) or " - ERROR - " in line or "✗" in line or "error" in low:
                return line.strip()
    except Exception:
        return None
    return None


def pytest_sessionstart(session):
    """Инициализируем накопитель результатов."""
    session.config._vt_results = []  # type: ignore[attr-defined]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Собираем результаты тестов и, для fail, пытаемся достать шаг ошибки из лога."""
    outcome = yield  # получаем отчёт
    report = outcome.get_result()

    # Интересует стадия выполнения тестового тела
    if report.when != "call":
        return

    nodeid = report.nodeid
    result = {
        "nodeid": nodeid,
        "outcome": report.outcome,
    }

    if report.failed:
        # Короткая причина из traceback (первую строку)
        longrepr = getattr(report, "longreprtext", "") or str(getattr(report, "longrepr", ""))
        reason = longrepr.strip().splitlines()[0] if longrepr else "Причина не определена"
        result["reason"] = reason

        # Пытаемся найти последний шаг/ошибку из логов тестового файла
        # Берём базовое имя файла из item.fspath
        try:
            test_file_base = os.path.splitext(os.path.basename(str(item.fspath)))[0]
            log_path = _find_latest_test_log_file(test_file_base)
            if log_path:
                step = _extract_last_step_or_error_from_log(log_path)
                if step:
                    result["failed_step"] = step
        except Exception:
            pass

    # Сохраняем
    item.config._vt_results.append(result)  # type: ignore[attr-defined]


def pytest_sessionfinish(session, exitstatus):
    """В конце сессии пишем summary, если выполнено более одного теста."""
    results = getattr(session.config, "_vt_results", [])  # type: ignore[attr-defined]
    if not results or len(results) <= 1:
        return

    os.makedirs("logs", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = os.path.join("logs", f"summary_{ts}.log")

    passed = [r for r in results if r.get("outcome") == "passed"]
    failed = [r for r in results if r.get("outcome") == "failed"]

    lines = []
    # Шапка с количеством
    total = len(results)
    lines.append(f"TOTAL: {total} | PASSED: {len(passed)} | FAILED: {len(failed)}")
    lines.append("")
    if passed:
        lines.append("PASSED:")
        for r in passed:
            lines.append(f"  - SUCCESS {r['nodeid']}")
        lines.append("")

    if failed:
        lines.append("FAILED:")
        for r in failed:
            lines.append(f"  - FAIL {r['nodeid']}")
            if r.get("reason"):
                lines.append(f"    Reason: {r['reason']}")
            if r.get("failed_step"):
                lines.append(f"    Step: {r['failed_step']}")
        lines.append("")
    else:
        lines.append("FAILED: none")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"Summary файл создан: {summary_path}")
