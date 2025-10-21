#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации автоматического определения медиа-устройств.
"""
import sys
from pathlib import Path

# Добавляем путь к utils для импорта
sys.path.insert(0, str(Path(__file__).parent))

from utils.config_manager import config
from utils.media_device_detector import MediaDeviceDetector


def test_media_detection():
    """Тестирует функционал автоматического определения медиа-устройств."""
    print("🧪 ТЕСТИРОВАНИЕ АВТОМАТИЧЕСКОГО ОПРЕДЕЛЕНИЯ МЕДИА-УСТРОЙСТВ")
    print("="*60)
    
    # Показываем текущую конфигурацию
    print("\n📋 ТЕКУЩАЯ КОНФИГУРАЦИЯ:")
    print(f"Video Device ID: {config.media.video_device_id[:20]}...")
    print(f"Audio Device ID: {config.media.audio_device_id[:20]}...")
    print(f"Camera: {config.media.camera_for_selection}")
    print(f"Microphone: {config.media.mic_for_selection}")
    
    # Создаем детектор
    print("\n🔍 Создание детектора медиа-устройств...")
    detector = MediaDeviceDetector(
        chrome_driver_path=config.browser.chrome_driver_path,
        chrome_browser_path=config.browser.chrome_browser_path
    )
    
    # Показываем доступные устройства
    print("\n📱 ДОСТУПНЫЕ УСТРОЙСТВА:")
    detector.print_available_devices()
    
    # Пытаемся найти предпочтительные устройства
    print("\n🎯 ПОИСК ПРЕДПОЧТИТЕЛЬНЫХ УСТРОЙСТВ:")
    video_id, audio_id = detector.get_preferred_devices(
        preferred_camera_name="LOGI",
        preferred_mic_name="LOGI"
    )
    
    if video_id and audio_id:
        print(f"✅ Найдены устройства:")
        print(f"📹 Video Device ID: {video_id}")
        print(f"🎤 Audio Device ID: {audio_id}")
        
        # Тестируем обновление конфигурации
        print("\n🔄 ТЕСТИРОВАНИЕ ОБНОВЛЕНИЯ КОНФИГУРАЦИИ:")
        success = config.detect_and_update_media_devices(
            preferred_camera_name="LOGI",
            preferred_mic_name="LOGI"
        )
        
        if success:
            print("✅ Конфигурация успешно обновлена!")
            print(f"📹 Новый Video Device ID: {config.media.video_device_id[:20]}...")
            print(f"🎤 Новый Audio Device ID: {config.media.audio_device_id[:20]}...")
        else:
            print("❌ Не удалось обновить конфигурацию")
    else:
        print("❌ Не удалось найти подходящие устройства")
    
    print("\n" + "="*60)
    print("🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")


if __name__ == "__main__":
    test_media_detection()
