#!/usr/bin/env python3
"""
Скрипт для автоматического определения и настройки медиа-устройств.
Позволяет найти доступные камеры и микрофоны, а также обновить конфигурацию.
"""
import sys
import os
import argparse
from pathlib import Path

# Добавляем путь к utils для импорта
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from utils.config_manager import config
from utils.media_device_detector import MediaDeviceDetector


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(
        description="Автоматическое определение и настройка медиа-устройств",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

1. Показать все доступные устройства:
   python scripts/detect_media_devices.py --list

2. Автоматически найти и обновить конфигурацию:
   python scripts/detect_media_devices.py --auto-detect

3. Найти устройства по названию:
   python scripts/detect_media_devices.py --camera "LOGI" --mic "LOGI"

4. Показать текущую конфигурацию:
   python scripts/detect_media_devices.py --show-config
        """
    )
    
    parser.add_argument(
        '--list', 
        action='store_true',
        help='Показать список всех доступных медиа-устройств'
    )
    
    parser.add_argument(
        '--auto-detect',
        action='store_true',
        help='Автоматически определить и обновить конфигурацию устройств'
    )
    
    parser.add_argument(
        '--camera',
        type=str,
        help='Название предпочтительной камеры (частичное совпадение)'
    )
    
    parser.add_argument(
        '--mic',
        type=str,
        help='Название предпочтительного микрофона (частичное совпадение)'
    )
    
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Показать текущую конфигурацию медиа-устройств'
    )
    
    parser.add_argument(
        '--update-config',
        action='store_true',
        help='Обновить конфигурацию найденными устройствами'
    )
    
    args = parser.parse_args()
    
    # Если не указаны аргументы, показываем справку
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    try:
        # Создаем детектор устройств
        detector = MediaDeviceDetector(
            chrome_driver_path=config.browser.chrome_driver_path,
            chrome_browser_path=config.browser.chrome_browser_path
        )
        
        # Показываем список устройств
        if args.list:
            print("🔍 Поиск доступных медиа-устройств...")
            detector.print_available_devices()
        
        # Показываем текущую конфигурацию
        if args.show_config:
            print("\n📋 ТЕКУЩАЯ КОНФИГУРАЦИЯ МЕДИА-УСТРОЙСТВ:")
            print("="*50)
            print(f"Video Device ID: {config.media.video_device_id}")
            print(f"Audio Device ID: {config.media.audio_device_id}")
            print(f"Camera: {config.media.camera_for_selection}")
            print(f"Microphone: {config.media.mic_for_selection}")
            print("="*50)
        
        # Автоматическое определение
        if args.auto_detect or args.camera or args.mic or args.update_config:
            print("🔍 Автоматическое определение медиа-устройств...")
            
            # Определяем предпочтительные названия
            camera_name = args.camera or config.media.camera_for_selection
            mic_name = args.mic or config.media.mic_for_selection
            
            # Ищем устройства
            video_id, audio_id = detector.get_preferred_devices(
                preferred_camera_name=camera_name,
                preferred_mic_name=mic_name
            )
            
            if video_id and audio_id:
                print(f"\n✅ Найдены устройства:")
                print(f"📹 Video Device ID: {video_id}")
                print(f"🎤 Audio Device ID: {audio_id}")
                
                # Обновляем конфигурацию если запрошено
                if args.update_config or args.auto_detect:
                    success = config.detect_and_update_media_devices(
                        preferred_camera_name=camera_name,
                        preferred_mic_name=mic_name
                    )
                    
                    if success:
                        print("\n✅ Конфигурация успешно обновлена!")
                        print("\n📋 ОБНОВЛЕННАЯ КОНФИГУРАЦИЯ:")
                        print("="*50)
                        print(f"Video Device ID: {config.media.video_device_id}")
                        print(f"Audio Device ID: {config.media.audio_device_id}")
                        print("="*50)
                        
                        # Показываем команды для установки переменных окружения
                        print("\n🔧 Для установки переменных окружения выполните:")
                        print(f'$env:VIDEO_DEVICE_ID = "{config.media.video_device_id}"')
                        print(f'$env:AUDIO_DEVICE_ID = "{config.media.audio_device_id}"')
                    else:
                        print("\n❌ Не удалось обновить конфигурацию")
            else:
                print("\n❌ Не удалось найти подходящие медиа-устройства")
                print("💡 Попробуйте использовать --list для просмотра всех доступных устройств")
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
