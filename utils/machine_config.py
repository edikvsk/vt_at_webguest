"""
Модуль для автоматического определения машины и загрузки соответствующей конфигурации.
"""
import os
import socket
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
import urllib.request
import urllib.error


class MachineDetector:
    """Класс для определения текущей машины."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_machine_name(self) -> str:
        """
        Определяет имя текущей машины.
        
        Returns:
            Имя машины (например, 'EDWARD', 'DEMOSTAND')
        """
        try:
            # Получаем имя компьютера
            machine_name = socket.gethostname().upper()
            self.logger.info(f"Определено имя машины: {machine_name}")
            return machine_name
        except Exception as e:
            self.logger.error(f"Ошибка при определении имени машины: {e}")
            return "UNKNOWN"
    
    def get_environment_name(self) -> str:
        """
        Определяет имя окружения на основе имени машины.
        
        Returns:
            Имя окружения для конфигурации
        """
        machine_name = self.get_machine_name()
        
        # Маппинг имен машин на окружения
        machine_mapping = {
            "EDWARD": "EDWARD",
            "DEMOSTAND": "DEMOSTAND"
        }
        
        # Проверяем точное совпадение
        if machine_name in machine_mapping:
            return machine_mapping[machine_name]
        
        # Проверяем частичное совпадение
        for env_name, mapped_name in machine_mapping.items():
            if env_name in machine_name or machine_name in env_name:
                self.logger.info(f"Найдено частичное совпадение: {machine_name} -> {mapped_name}")
                return mapped_name
        
        # Если ничего не найдено, используем DEFAULT (A4)
        self.logger.info(f"Машина '{machine_name}' не найдена в конфигурации, используется DEFAULT (A4)")
        return "DEFAULT"


class ConfigLoader:
    """Класс для загрузки конфигурации из различных источников."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.machine_detector = MachineDetector()
    
    def load_config_from_network(self, network_path: str) -> Optional[Dict[str, Any]]:
        """
        Загружает конфигурацию с сетевого пути.
        
        Args:
            network_path: Путь к файлу конфигурации (например, \\\\192.168.10.100\\web\\VT_WebGuest_config\\appconfig.json)
            
        Returns:
            Словарь с конфигурацией или None при ошибке
        """
        try:
            # Нормализуем UNC путь
            if network_path.startswith('\\\\'):
                # Уже корректный UNC путь
                config_url = f"file:///{network_path.replace('\\\\', '/')}"
            else:
                # Добавляем префикс UNC
                config_url = f"file:///{network_path.replace('\\', '/')}"
            
            self.logger.info(f"Загружаю конфигурацию с сетевого пути: {network_path}")
            
            # Пытаемся загрузить как файл
            try:
                with open(network_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.logger.info("Конфигурация успешно загружена с сетевого пути")
                    return config
            except FileNotFoundError:
                self.logger.warning(f"Файл конфигурации не найден по пути: {network_path}")
                return None
            except json.JSONDecodeError as e:
                self.logger.error(f"Ошибка парсинга JSON файла: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке конфигурации с сетевого пути: {e}")
            return None
    
    def load_config_from_local(self, local_path: str) -> Optional[Dict[str, Any]]:
        """
        Загружает конфигурацию из локального файла.
        
        Args:
            local_path: Путь к локальному файлу конфигурации
            
        Returns:
            Словарь с конфигурацией или None при ошибке
        """
        try:
            config_path = Path(local_path)
            if not config_path.exists():
                self.logger.warning(f"Локальный файл конфигурации не найден: {local_path}")
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.logger.info("Конфигурация успешно загружена из локального файла")
                return config
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON файла: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке локальной конфигурации: {e}")
            return None
    
    def get_environment_config(self, config: Dict[str, Any], environment_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Получает конфигурацию для конкретного окружения.
        
        Args:
            config: Общая конфигурация
            environment_name: Имя окружения (если None, определяется автоматически)
            
        Returns:
            Конфигурация окружения или None
        """
        if environment_name is None:
            environment_name = self.machine_detector.get_environment_name()
        
        environments = config.get('environments', {})
        
        if environment_name in environments:
            env_config = environments[environment_name]
            self.logger.info(f"Загружена конфигурация для окружения: {environment_name}")
            return env_config
        else:
            # Пытаемся использовать окружение по умолчанию
            default_env = config.get('default_environment')
            if default_env and default_env in environments:
                self.logger.warning(f"Окружение '{environment_name}' не найдено, используется '{default_env}'")
                return environments[default_env]
            else:
                self.logger.error(f"Окружение '{environment_name}' не найдено и нет окружения по умолчанию")
                return None
    
    def load_config(self, network_path: str) -> Optional[Dict[str, Any]]:
        """
        Загружает конфигурацию только с сетевого пути.
        
        Args:
            network_path: Путь к сетевому файлу конфигурации
            
        Returns:
            Конфигурация окружения или None
        """
        # Загружаем только с сетевого пути
        config = self.load_config_from_network(network_path)
        
        # Если не удалось загрузить с сетевого пути, используем встроенную конфигурацию
        if config is None:
            self.logger.warning("Не удалось загрузить конфигурацию с сетевого пути, используется встроенная")
            config = self._get_default_config()
        
        if config is None:
            return None
        
        # Получаем конфигурацию для текущего окружения
        return self.get_environment_config(config)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Возвращает встроенную конфигурацию по умолчанию.
        
        Returns:
            Встроенная конфигурация
        """
        return {
            "environments": {
                "EDWARD": {
                    "description": "Машина EDWARD с устройствами Logitech",
                    "media_devices": {
                        "camera_for_selection": "Logi",
                        "mic_for_selection": "Logi",
                        "video_device_id": "",
                        "audio_device_id": ""
                    }
                },
                "DEMOSTAND": {
                    "description": "Машина DEMOSTAND с устройствами A4",
                    "media_devices": {
                        "camera_for_selection": "A4",
                        "mic_for_selection": "A4",
                        "video_device_id": "",
                        "audio_device_id": ""
                    }
                },
                "DEFAULT": {
                    "description": "Конфигурация по умолчанию с устройствами A4",
                    "media_devices": {
                        "camera_for_selection": "A4",
                        "mic_for_selection": "A4",
                        "video_device_id": "",
                        "audio_device_id": ""
                    }
                }
            },
            "default_environment": "DEFAULT",
            "config_version": "1.0",
            "last_updated": "2024-01-01"
        }


# Глобальные экземпляры
machine_detector = MachineDetector()
config_loader = ConfigLoader()
