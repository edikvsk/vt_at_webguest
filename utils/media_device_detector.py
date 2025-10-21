"""
Модуль для автоматического определения медиа-устройств (камера и микрофон).
Использует WebDriver для получения списка доступных устройств через JavaScript.
"""
import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException


@dataclass
class MediaDevice:
    """Информация о медиа-устройстве."""
    device_id: str
    label: str
    kind: str  # 'videoinput' или 'audioinput'
    group_id: str


class MediaDeviceDetector:
    """Класс для автоматического определения доступных медиа-устройств."""
    
    def __init__(self, chrome_driver_path: str, chrome_browser_path: str):
        """
        Инициализация детектора медиа-устройств.
        
        Args:
            chrome_driver_path: Путь к ChromeDriver
            chrome_browser_path: Путь к Chrome браузеру
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.chrome_driver_path = chrome_driver_path
        self.chrome_browser_path = chrome_browser_path
        self._driver: Optional[webdriver.Chrome] = None
    
    def _create_driver(self) -> webdriver.Chrome:
        """Создает WebDriver для определения устройств."""
        chrome_options = Options()
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        chrome_options.add_argument("--enable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--unsafely-treat-insecure-origin-as-secure=http://localhost")
        chrome_options.add_argument("--allow-http-screen-capture")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.binary_location = self.chrome_browser_path
        
        service = Service(self.chrome_driver_path)
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def _get_devices_script(self) -> str:
        """Возвращает JavaScript код для получения списка медиа-устройств."""
        return """
        return new Promise((resolve, reject) => {
            // Проверяем поддержку MediaDevices API
            if (!navigator.mediaDevices) {
                reject('MediaDevices API not supported');
                return;
            }
            
            // Сначала запрашиваем разрешения для доступа к устройствам
            navigator.mediaDevices.getUserMedia({ video: true, audio: true })
                .then(stream => {
                    // Останавливаем поток
                    stream.getTracks().forEach(track => track.stop());
                    
                    // Теперь получаем список устройств
                    return navigator.mediaDevices.enumerateDevices();
                })
                .then(devices => {
                    const deviceList = devices.map(device => ({
                        deviceId: device.deviceId,
                        label: device.label || 'Unknown Device',
                        kind: device.kind,
                        groupId: device.groupId
                    }));
                    resolve(deviceList);
                })
                .catch(err => {
                    // Если getUserMedia не работает, пробуем без него
                    if (navigator.mediaDevices.enumerateDevices) {
                        navigator.mediaDevices.enumerateDevices()
                            .then(devices => {
                                const deviceList = devices.map(device => ({
                                    deviceId: device.deviceId,
                                    label: device.label || 'Unknown Device',
                                    kind: device.kind,
                                    groupId: device.groupId
                                }));
                                resolve(deviceList);
                            })
                            .catch(err2 => reject(err2));
                    } else {
                        reject(err);
                    }
                });
        });
        """
    
    def detect_devices(self) -> Tuple[List[MediaDevice], List[MediaDevice]]:
        """
        Определяет доступные видео и аудио устройства.
        
        Returns:
            Кортеж (video_devices, audio_devices)
        """
        video_devices = []
        audio_devices = []
        
        try:
            self._driver = self._create_driver()
            self.logger.info("Запуск браузера для определения медиа-устройств...")
            
            # Открываем простую HTML страницу через localhost
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Media Device Detection</title>
            </head>
            <body>
                <h1>Media Device Detection</h1>
                <p>Detecting media devices...</p>
            </body>
            </html>
            """
            
            # Создаем временный HTML файл
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_content)
                temp_file = f.name
            
            # Открываем файл через file:// протокол
            self._driver.get(f"file://{temp_file}")
            
            # Удаляем временный файл
            import os
            try:
                os.unlink(temp_file)
            except:
                pass
            
            # Ждем загрузки страницы
            time.sleep(2)
            
            # Выполняем JavaScript для получения устройств
            self.logger.info("Получение списка медиа-устройств...")
            devices_data = self._driver.execute_script(self._get_devices_script())
            
            if not devices_data:
                self.logger.warning("Не удалось получить данные об устройствах")
                return video_devices, audio_devices
            
            # Обрабатываем полученные данные
            for device_data in devices_data:
                device = MediaDevice(
                    device_id=device_data['deviceId'],
                    label=device_data['label'],
                    kind=device_data['kind'],
                    group_id=device_data['groupId']
                )
                
                if device.kind == 'videoinput':
                    video_devices.append(device)
                elif device.kind == 'audioinput':
                    audio_devices.append(device)
            
            self.logger.info(f"Найдено {len(video_devices)} видео устройств и {len(audio_devices)} аудио устройств")
            
        except WebDriverException as e:
            self.logger.error(f"Ошибка WebDriver при определении устройств: {e}")
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при определении устройств: {e}")
        finally:
            if self._driver:
                try:
                    self._driver.quit()
                except Exception as e:
                    self.logger.warning(f"Ошибка при закрытии браузера: {e}")
        
        return video_devices, audio_devices
    
    def get_preferred_devices(self, 
                            preferred_camera_name: Optional[str] = None,
                            preferred_mic_name: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Возвращает ID предпочтительных устройств на основе их названий.
        
        Args:
            preferred_camera_name: Название предпочтительной камеры (частичное совпадение)
            preferred_mic_name: Название предпочтительного микрофона (частичное совпадение)
            
        Returns:
            Кортеж (video_device_id, audio_device_id)
        """
        video_devices, audio_devices = self.detect_devices()
        
        video_device_id = None
        audio_device_id = None
        found_camera = None
        found_mic = None
        
        # Поиск видео устройства
        if preferred_camera_name:
            self.logger.info(f"Поиск камеры с названием содержащим: '{preferred_camera_name}'")
            for device in video_devices:
                if preferred_camera_name.lower() in device.label.lower():
                    video_device_id = device.device_id
                    found_camera = device
                    self.logger.info(f"✅ Найдена предпочтительная камера: {device.label}")
                    self.logger.info(f"   ID: {device.device_id}")
                    break
        
        # Если не найдена предпочтительная камера, берем первую доступную
        if not video_device_id and video_devices:
            video_device_id = video_devices[0].device_id
            found_camera = video_devices[0]
            self.logger.info(f"⚠️ Используется первая доступная камера: {video_devices[0].label}")
        
        # Поиск аудио устройства
        if preferred_mic_name:
            self.logger.info(f"Поиск микрофона с названием содержащим: '{preferred_mic_name}'")
            for device in audio_devices:
                if preferred_mic_name.lower() in device.label.lower():
                    audio_device_id = device.device_id
                    found_mic = device
                    self.logger.info(f"✅ Найден предпочтительный микрофон: {device.label}")
                    self.logger.info(f"   ID: {device.device_id}")
                    break
        
        # Если не найден предпочтительный микрофон, берем первый доступный
        if not audio_device_id and audio_devices:
            audio_device_id = audio_devices[0].device_id
            found_mic = audio_devices[0]
            self.logger.info(f"⚠️ Используется первый доступный микрофон: {audio_devices[0].label}")
        
        # Выводим итоговую информацию
        if found_camera:
            print(f"\n📹 ВЫБРАННАЯ КАМЕРА: {found_camera.label}")
            print(f"   ID: {found_camera.device_id}")
        
        if found_mic:
            print(f"\n🎤 ВЫБРАННЫЙ МИКРОФОН: {found_mic.label}")
            print(f"   ID: {found_mic.device_id}")
        
        return video_device_id, audio_device_id
    
    def print_available_devices(self) -> None:
        """Выводит список всех доступных медиа-устройств."""
        video_devices, audio_devices = self.detect_devices()
        
        print("\n" + "="*60)
        print("ДОСТУПНЫЕ МЕДИА-УСТРОЙСТВА")
        print("="*60)
        
        print(f"\n📹 ВИДЕО УСТРОЙСТВА ({len(video_devices)}):")
        for i, device in enumerate(video_devices, 1):
            print(f"  {i}. {device.label}")
            print(f"     ID: {device.device_id}")
            print(f"     Group: {device.group_id}")
            print()
        
        print(f"\n🎤 АУДИО УСТРОЙСТВА ({len(audio_devices)}):")
        for i, device in enumerate(audio_devices, 1):
            print(f"  {i}. {device.label}")
            print(f"     ID: {device.device_id}")
            print(f"     Group: {device.group_id}")
            print()
        
        print("="*60 + "\n")
    
    def get_device_info_by_id(self, device_id: str) -> Optional[MediaDevice]:
        """
        Получает информацию об устройстве по его ID.
        
        Args:
            device_id: ID устройства
            
        Returns:
            Информация об устройстве или None если не найдено
        """
        video_devices, audio_devices = self.detect_devices()
        all_devices = video_devices + audio_devices
        
        for device in all_devices:
            if device.device_id == device_id:
                return device
        
        return None


def main():
    """Основная функция для тестирования детектора устройств."""
    import sys
    from pathlib import Path
    
    # Добавляем путь к utils для импорта
    utils_path = Path(__file__).parent
    sys.path.insert(0, str(utils_path.parent))
    
    from utils.config_manager import config
    
    # Создаем детектор
    detector = MediaDeviceDetector(
        chrome_driver_path=config.browser.chrome_driver_path,
        chrome_browser_path=config.browser.chrome_browser_path
    )
    
    # Выводим доступные устройства
    detector.print_available_devices()
    
    # Пытаемся найти предпочтительные устройства
    video_id, audio_id = detector.get_preferred_devices(
        preferred_camera_name="LOGI",  # Ищем камеру Logitech
        preferred_mic_name="LOGI"      # Ищем микрофон Logitech
    )
    
    if video_id:
        print(f"Рекомендуемый Video Device ID: {video_id}")
    if audio_id:
        print(f"Рекомендуемый Audio Device ID: {audio_id}")


if __name__ == "__main__":
    main()
