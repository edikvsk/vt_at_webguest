import os

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage
from pages.desktop_app_page import DesktopAppPage
from pages.web_guest_page import WebGuestPage
from utils.conftest import driver, login_fixture
from utils.desktop_app import DesktopApp
from utils.helpers import log_step
from utils.logger_config import setup_logger
from utils.notificaton_handler import NotificationHandler
from utils.webrtc_stream_handler import StreamHandler
from utils.urls import PROCESS_PATH


@pytest.fixture(scope="function")
def logger(caplog):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = setup_logger(test_name)
    return logger


@pytest.mark.usefixtures("login_fixture")
def test_framerate_15fps(driver, logger):
    wg_page = WebGuestPage(driver)
    base_page = BasePage(driver)
    stream_handler = StreamHandler(driver)
    notification_handler = NotificationHandler(driver, wg_page.NOTIFICATION_ELEMENT, logger)
    desktop_app = DesktopApp(PROCESS_PATH)
    desktop_app_page = DesktopAppPage(desktop_app.main_window)

    vt_web_guest_source_name = "Web Guest"
    framerate = "15 FPS"

    @log_step(logger, "ШАГ 1. Проверка отображения кнопки SETTINGS")
    def check_settings_button():
        assert base_page.is_element_present(wg_page.SETTINGS_BUTTON), "Кнопка SETTINGS не отображается"

    @log_step(logger, "ШАГ 2. Нажатие кнопки SETTINGS")
    def click_settings_button():
        wg_page.click_element_with_scroll(wg_page.SETTINGS_BUTTON)
        assert wg_page.is_element_visible(wg_page.WG_SETTINGS_WINDOW), "Settings не открыты"

    @log_step(logger, "ШАГ 3. Выбор Framerate")
    def select_framerate():
        wg_page.select_framerate(framerate)
        notification_handler.check_notification()
        base_page.click(wg_page.COMBOBOX_BACK_BUTTON)
        expected_value = framerate
        actual_value = wg_page.get_settings_item_value_text(wg_page.FRAMERATE_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 4. Проверка значения Framerate в VT WebGuest Settings")
    def check_framerate_field_value_vt():
        desktop_app_page.right_click_vt_source_item(vt_web_guest_source_name)
        desktop_app_page.click_vt_source_item(DesktopAppPage.VT_WEB_GUEST_SETTINGS)
        desktop_app_page.select_combobox_item_by_index(1, 0)
        desktop_app_page.click_button_by_name(DesktopAppPage.VT_OK_BUTTON)

    @log_step(logger, "ШАГ 5. Проверка значения поля Framerate")
    def check_framerate_field_value():
        expected_value = framerate
        actual_value = wg_page.get_settings_item_value_text(wg_page.FRAMERATE_VALUE)
        assert actual_value == expected_value, f"Ожидалось значение '{expected_value}', но получено '{actual_value}'"

    @log_step(logger, "ШАГ 6. Проверка значения Framerate в WebRTC")
    def check_webrtc_framerate():
        base_page.click(wg_page.STOP_BUTTON)
        base_page.click(wg_page.START_BUTTON)
        result = stream_handler.get_video_frame_rate()

        # Получаем значения FPS
        average_framerate = result['average_frame_rate']
        max_framerate = result['max_frame_rate']

        # Форматируем максимальную частоту кадров
        formatted_framerate = stream_handler.format_frame_rate(max_framerate)

        logger.info(f'Average Framerate: {average_framerate:.2f} FPS')  # Форматируем вывод
        logger.info(f'Max Framerate: {formatted_framerate} FPS')  # Используем отформатированное значение

        assert formatted_framerate == framerate, (f"Ожидалось значение '{framerate}',"
                                                  f" но получено '{formatted_framerate}'")

    steps = [
        check_settings_button,
        click_settings_button,
        select_framerate,
        check_framerate_field_value_vt,
        check_framerate_field_value,
        check_webrtc_framerate
    ]

    for step in steps:
        try:
            step()
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Ошибка при выполнении теста: {e}")
            pytest.fail(f"Ошибка при выполнении теста: {e}")

        # При необходимости закрыть VT
        # finally:

        # desktop_app.close_application()
