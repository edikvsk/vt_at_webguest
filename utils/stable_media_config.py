"""
Модуль для стабильной конфигурации медиа-устройств.
Использует названия устройств вместо ID для более надежной работы.
"""
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Добавляем путь к utils для импорта
utils_path = Path(__file__).parent
sys.path.insert(0, str(utils_path.parent))

from utils.media_device_detector import MediaDeviceDetector, MediaDevice


@dataclass
class StableMediaConfig:
    """Стабильная конфигурация медиа-устройств на основе названий."""
    camera_name: str
    microphone_name: str
    video_device_id: Optional[str] = None
    audio_device_id: Optional[str] = None


class StableMediaManager:
    """Менеджер для стабильной работы с медиа-устройствами."""
    
    def __init__(self, chrome_driver_path: str, chrome_browser_path: str):
        """
        Инициализация менеджера.
        
        Args:
            chrome_driver_path: Путь к ChromeDriver
            chrome_browser_path: Путь к Chrome браузеру
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.detector = MediaDeviceDetector(chrome_driver_path, chrome_browser_path)
        self._device_cache: Dict[str, str] = {}
    
    def get_device_id_by_name(self, device_name: str, device_type: str) -> Optional[str]:
        """
        Получает ID устройства по его названию.
        
        Args:
            device_name: Название устройства (частичное совпадение)
            device_type: Тип устройства ('video' или 'audio')
            
        Returns:
            ID устройства или None если не найдено
        """
        # Проверяем кэш
        cache_key = f"{device_type}_{device_name}"
        if cache_key in self._device_cache:
            return self._device_cache[cache_key]
        
        # Получаем список устройств
        video_devices, audio_devices = self.detector.detect_devices()
        
        devices = video_devices if device_type == 'video' else audio_devices
        
        # Ищем устройство по названию
        for device in devices:
            if device_name.lower() in device.label.lower():
                self._device_cache[cache_key] = device.device_id
                self.logger.info(f"Найдено {device_type} устройство: {device.label} -> {device.device_id}")
                return device.device_id
        
        self.logger.warning(f"Не найдено {device_type} устройство с названием содержащим: {device_name}")
        return None
    
    def get_media_constraints(self, camera_name: str, mic_name: str) -> Dict[str, Any]:
        """
        Получает media_constraints для указанных устройств.
        
        Args:
            camera_name: Название камеры
            mic_name: Название микрофона
            
        Returns:
            Словарь с media_constraints
        """
        video_id = self.get_device_id_by_name(camera_name, 'video')
        audio_id = self.get_device_id_by_name(mic_name, 'audio')
        
        constraints = {}
        
        if video_id:
            constraints['video'] = {"deviceId": {"exact": video_id}}
        else:
            constraints['video'] = True  # Используем первую доступную камеру
        
        if audio_id:
            constraints['audio'] = {"deviceId": {"exact": audio_id}}
        else:
            constraints['audio'] = True  # Используем первый доступный микрофон
        
        return constraints
    
    def clear_cache(self):
        """Очищает кэш устройств."""
        self._device_cache.clear()
        self.logger.info("Кэш устройств очищен")
    
    def print_current_devices(self, camera_name: str, mic_name: str):
        """
        Выводит информацию о текущих устройствах.
        
        Args:
            camera_name: Название камеры
            mic_name: Название микрофона
        """
        video_id = self.get_device_id_by_name(camera_name, 'video')
        audio_id = self.get_device_id_by_name(mic_name, 'audio')
        
        print(f"\n📹 КАМЕРА: {camera_name}")
        if video_id:
            print(f"   ID: {video_id}")
        else:
            print("   ❌ Не найдена")
        
        print(f"\n🎤 МИКРОФОН: {mic_name}")
        if audio_id:
            print(f"   ID: {audio_id}")
        else:
            print("   ❌ Не найден")
        
        if video_id and audio_id:
            print(f"\n✅ Media Constraints:")
            constraints = self.get_media_constraints(camera_name, mic_name)
            print(f"   {constraints}")
        else:
            print(f"\n❌ Не удалось создать media_constraints")


def main():
    """Основная функция для тестирования."""
    import sys
    from pathlib import Path
    
    # Добавляем путь к utils для импорта
    utils_path = Path(__file__).parent
    sys.path.insert(0, str(utils_path.parent))
    
    from utils.config_manager import config
    
    # Создаем менеджер
    manager = StableMediaManager(
        chrome_driver_path=config.browser.chrome_driver_path,
        chrome_browser_path=config.browser.chrome_browser_path
    )
    
    # Тестируем с камерой Logi
    print("🧪 ТЕСТИРОВАНИЕ СТАБИЛЬНОЙ КОНФИГУРАЦИИ МЕДИА-УСТРОЙСТВ")
    print("="*60)
    
    manager.print_current_devices("Logi", "Logi")
    
    # Получаем media_constraints
    constraints = manager.get_media_constraints("Logi", "Logi")
    print(f"\n🎯 ИТОГОВЫЕ MEDIA_CONSTRAINTS:")
    print(f"   {constraints}")


if __name__ == "__main__":
    main()
