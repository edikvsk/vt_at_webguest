#!/usr/bin/env python3
"""
Скрипт для тестирования и демонстрации работы с медиа-устройствами.
Позволяет просмотреть доступные устройства и найти их по имени.
"""
import sys
import os
import logging

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.device_manager import device_manager
from utils.config_manager import config


def setup_logging():
    """Настраивает логирование."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Основная функция."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("="*60)
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ АВТОМАТИЧЕСКОГО ВЫБОРА УСТРОЙСТВ")
    print("="*60)
    
    # Показываем все доступные устройства
    print("\n1. Просмотр всех доступных устройств:")
    device_manager.list_devices()
    
    # Тестируем поиск устройств по имени
    print("\n2. Тестирование поиска устройств по имени:")
    
    # Получаем имена устройств из конфигурации
    camera_name = config.media.camera_for_selection
    mic_name = config.media.mic_for_selection
    
    print(f"   Ищем камеру по имени: '{camera_name}'")
    video_device = device_manager.find_video_device_by_name(camera_name)
    if video_device:
        print(f"   ✓ Найдена камера: {video_device.label}")
        print(f"     ID: {video_device.device_id[:30]}...")
    else:
        print(f"   ✗ Камера с именем '{camera_name}' не найдена")
    
    print(f"   Ищем микрофон по имени: '{mic_name}'")
    audio_device = device_manager.find_audio_device_by_name(mic_name)
    if audio_device:
        print(f"   ✓ Найден микрофон: {audio_device.label}")
        print(f"     ID: {audio_device.device_id[:30]}...")
    else:
        print(f"   ✗ Микрофон с именем '{mic_name}' не найден")
    
    # Показываем текущую конфигурацию
    print("\n3. Текущая конфигурация:")
    config.print_config_summary()
    
    # Тестируем поиск с разными именами
    print("\n4. Тестирование поиска с разными именами:")
    test_names = ["Logi", "Camera", "Microphone", "USB", "HD"]
    
    for name in test_names:
        video_device = device_manager.find_video_device_by_name(name)
        audio_device = device_manager.find_audio_device_by_name(name)
        
        print(f"   Поиск по '{name}':")
        if video_device:
            print(f"     Видео: {video_device.label}")
        else:
            print(f"     Видео: не найдено")
            
        if audio_device:
            print(f"     Аудио: {audio_device.label}")
        else:
            print(f"     Аудио: не найдено")
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)


if __name__ == "__main__":
    main()
