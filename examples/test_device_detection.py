"""
Пример использования новой системы автоматического выбора устройств.
Этот файл демонстрирует, как работает автоматическое определение ID устройств.
"""
import os
import sys
import logging

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.device_manager import device_manager
from utils.config_manager import config


def test_device_detection():
    """Тестирует автоматическое определение устройств."""
    print("="*60)
    print("ТЕСТ АВТОМАТИЧЕСКОГО ОПРЕДЕЛЕНИЯ УСТРОЙСТВ")
    print("="*60)
    
    # Устанавливаем переменные окружения для теста
    os.environ['CAMERA_FOR_SELECTION'] = 'Logi'
    os.environ['MIC_FOR_SELECTION'] = 'Logi'
    
    # Перезагружаем конфигурацию
    config._load_config()
    
    print(f"\n1. Поиск камеры по имени 'Logi':")
    camera = device_manager.find_video_device_by_name('Logi')
    if camera:
        print(f"   ✓ Найдена: {camera.label}")
        print(f"   ID: {camera.device_id[:30]}...")
    else:
        print("   ✗ Камера не найдена")
    
    print(f"\n2. Поиск микрофона по имени 'Logi':")
    mic = device_manager.find_audio_device_by_name('Logi')
    if mic:
        print(f"   ✓ Найден: {mic.label}")
        print(f"   ID: {mic.device_id[:30]}...")
    else:
        print("   ✗ Микрофон не найден")
    
    print(f"\n3. Текущая конфигурация:")
    print(f"   Video Device ID: {config.media.video_device_id[:30]}...")
    print(f"   Audio Device ID: {config.media.audio_device_id[:30]}...")
    print(f"   Camera Name: {config.media.camera_for_selection}")
    print(f"   Mic Name: {config.media.mic_for_selection}")
    
    print("\n" + "="*60)
    print("ТЕСТ ЗАВЕРШЕН")
    print("="*60)


if __name__ == "__main__":
    test_device_detection()
