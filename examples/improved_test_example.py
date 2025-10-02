"""
Пример улучшенного автотеста с использованием новых возможностей фреймворка.
"""
import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, login_fixture, test_logger
from utils.helpers import log_step, retry_on_failure, StepManager
from utils.test_data import test_data, Resolution, FrameRate
from utils.config_manager import config


@pytest.mark.smoke
@pytest.mark.stream_controls
@pytest.mark.fast
def test_improved_stream_start(driver, login_fixture, test_logger):
    """
    Улучшенный тест запуска стрима с использованием новых возможностей.
    
    Демонстрирует:
    - Использование StepManager для управления шагами
    - Централизованные тестовые данные
    - Улучшенное логирование
    - Retry механизм
    """
    # Инициализация
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    step_manager = StepManager(test_logger)
    
    # Получаем тестовые данные
    stream_settings = test_data.get_stream_settings_combinations()[0]  # Стандартные настройки
    
    # Начинаем тест
    step_manager.start_test(total_steps=5)
    
    try:
        # Шаг 1: Проверка отображения кнопки STOP
        step_manager.execute_step(
            "Проверка отображения кнопки STOP",
            lambda: assert base_page.is_element_present(wg_page.STOP_BUTTON, timeout=config.test.default_timeout),
        )
        
        # Шаг 2: Проверка состояния кнопки с retry
        @retry_on_failure(max_attempts=config.test.retry_count, logger=test_logger)
        def check_stop_button_state():
            return wg_page.is_button_pressed(wg_page.STOP_BUTTON)
        
        step_manager.execute_step(
            "Проверка состояния кнопки STOP",
            lambda: assert check_stop_button_state(),
        )
        
        # Шаг 3: Остановка стрима
        step_manager.execute_step(
            "Остановка трансляции",
            lambda: base_page.click(wg_page.STOP_BUTTON, timeout=config.test.long_timeout)
        )
        
        # Шаг 4: Проверка состояния после остановки
        step_manager.execute_step(
            "Проверка кнопки START после остановки",
            lambda: assert wg_page.is_button_pressed(wg_page.START_BUTTON)
        )
        
        # Шаг 5: Повторный запуск
        step_manager.execute_step(
            "Повторный запуск стрима",
            lambda: base_page.click(wg_page.START_BUTTON, timeout=config.test.long_timeout)
        )
        
    except (NoSuchElementException, TimeoutException) as e:
        test_logger.error(f"Ошибка при выполнении теста: {e}")
        pytest.fail(f"Ошибка при выполнении теста: {e}")
    finally:
        step_manager.finish_test()


@pytest.mark.smoke
@pytest.mark.wg_settings
@pytest.mark.parametrize("resolution", [Resolution.HD_720P, Resolution.FULL_HD, Resolution.SD_480P])
def test_resolution_settings_parametrized(driver, login_fixture, test_logger, resolution):
    """
    Параметризованный тест настроек разрешения.
    
    Args:
        resolution: Разрешение из enum Resolution
    """
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    
    test_logger.info(f"Тестирование разрешения: {resolution.value}")
    
    @log_step(test_logger, f"Открытие настроек для разрешения {resolution.value}")
    def open_settings():
        assert base_page.click(wg_page.SETTINGS_BUTTON), "Не удалось открыть настройки"
        assert base_page.is_element_visible(wg_page.WG_SETTINGS_WINDOW), "Окно настроек не открылось"
    
    @log_step(test_logger, f"Установка разрешения {resolution.value}")
    def set_resolution():
        wg_page.select_resolution(resolution.value)
        base_page.click(wg_page.COMBOBOX_BACK_BUTTON)
    
    @log_step(test_logger, f"Проверка установленного разрешения {resolution.value}")
    def verify_resolution():
        actual_value = wg_page.get_settings_item_value_text(wg_page.RESOLUTION_VALUE)
        assert actual_value == resolution.value, f"Ожидалось {resolution.value}, получено {actual_value}"
    
    # Выполняем шаги
    open_settings()
    set_resolution()
    verify_resolution()


@pytest.mark.negative
@pytest.mark.security
def test_negative_login_scenarios(driver, test_logger):
    """
    Тест негативных сценариев авторизации с использованием тестовых данных.
    """
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    
    # Получаем негативные сценарии
    negative_scenarios = test_data.get_negative_test_scenarios()
    
    for scenario in negative_scenarios:
        if "login" not in scenario.tags:
            continue
            
        test_logger.info(f"Выполнение сценария: {scenario.description}")
        
        # Переходим на страницу (здесь должен быть URL)
        # driver.get(web_guest_url)
        
        # Очищаем поля
        if scenario.user_credentials.name == "":
            wg_page.delete_text(wg_page.LOGIN_FIELD)
        else:
            base_page.send_keys(wg_page.LOGIN_FIELD, scenario.user_credentials.name)
            
        if scenario.user_credentials.location == "":
            wg_page.delete_text(wg_page.LOCATION_FIELD)
        else:
            base_page.send_keys(wg_page.LOCATION_FIELD, scenario.user_credentials.location)
        
        # Попытка входа
        base_page.click(wg_page.LOGIN_BUTTON)
        
        # Проверка ожидаемого результата
        if "Please provide name" in scenario.expected_result:
            assert base_page.is_element_visible(wg_page.AUTHORIZATION_NAME_FIELD_ERROR)
        elif "Please provide location" in scenario.expected_result:
            assert base_page.is_element_visible(wg_page.AUTHORIZATION_LOCATION_FIELD_ERROR)
        
        test_logger.info(f"Сценарий '{scenario.name}' выполнен успешно")


@pytest.mark.slow
@pytest.mark.stream_controls
@pytest.mark.requires_camera
@pytest.mark.requires_microphone
def test_comprehensive_stream_quality(driver, login_fixture, test_logger):
    """
    Комплексный тест качества стрима с проверкой всех параметров.
    """
    from utils.webrtc_stream_handler import StreamHandler
    
    wg_page = WebGuestPage(driver)
    stream_handler = StreamHandler(driver)
    step_manager = StepManager(test_logger)
    
    # Получаем настройки высокого качества
    hq_settings = test_data.get_stream_settings_combinations()[1]  # Высокое качество
    
    step_manager.start_test(total_steps=4)
    
    # Шаг 1: Проверка активности стрима
    step_manager.execute_step(
        "Проверка активности аудио и видео потоков",
        lambda: (
            assert stream_handler.is_audio_stream_active(),
            assert stream_handler.is_video_stream_active()
        )
    )
    
    # Шаг 2: Измерение качества видео
    step_manager.execute_step(
        "Измерение качества видео",
        lambda: check_video_quality(stream_handler, test_logger)
    )
    
    # Шаг 3: Измерение качества аудио
    step_manager.execute_step(
        "Измерение качества аудио",
        lambda: check_audio_quality(stream_handler, test_logger)
    )
    
    # Шаг 4: Проверка стабильности
    step_manager.execute_step(
        "Проверка стабильности стрима (30 секунд)",
        lambda: check_stream_stability(stream_handler, test_logger, duration=30)
    )
    
    step_manager.finish_test()


def check_video_quality(stream_handler, logger):
    """Проверяет качество видео."""
    # Получаем характеристики видео
    frame_rate_data = stream_handler.get_video_frame_rate()
    dimensions = stream_handler.get_video_frame_dimensions()
    bitrate_data = stream_handler.start_monitoring_video_bitrate()
    
    logger.info(f"Параметры видео:")
    logger.info(f"  - FPS: {frame_rate_data.get('average_frame_rate', 'N/A')}")
    logger.info(f"  - Разрешение: {dimensions}")
    logger.info(f"  - Битрейт: {bitrate_data.get('averageVideo', 'N/A')} Mbps")
    
    # Проверяем минимальные требования
    avg_fps = frame_rate_data.get('average_frame_rate', 0)
    assert avg_fps > 10, f"FPS слишком низкий: {avg_fps}"


def check_audio_quality(stream_handler, logger):
    """Проверяет качество аудио."""
    bitrate_data = stream_handler.start_monitoring_audio_bitrate()
    
    logger.info(f"Параметры аудио:")
    logger.info(f"  - Битрейт: {bitrate_data.get('averageAudio', 'N/A')} Kbps")
    
    # Проверяем минимальные требования
    avg_bitrate = float(bitrate_data.get('averageAudio', 0))
    assert avg_bitrate > 32, f"Аудио битрейт слишком низкий: {avg_bitrate}"


def check_stream_stability(stream_handler, logger, duration=30):
    """Проверяет стабильность стрима."""
    import time
    
    start_time = time.time()
    checks = 0
    failures = 0
    
    while time.time() - start_time < duration:
        if stream_handler.is_webrtc_connected():
            checks += 1
        else:
            failures += 1
            logger.warning("Обнаружен разрыв соединения")
        
        time.sleep(1)
    
    stability_ratio = (checks - failures) / checks if checks > 0 else 0
    logger.info(f"Стабильность стрима: {stability_ratio:.2%} ({checks-failures}/{checks} проверок)")
    
    assert stability_ratio > 0.95, f"Стабильность стрима недостаточна: {stability_ratio:.2%}"


if __name__ == "__main__":
    # Пример запуска отдельных тестов
    pytest.main([
        __file__ + "::test_improved_stream_start",
        "-v",
        "--tb=short"
    ])
