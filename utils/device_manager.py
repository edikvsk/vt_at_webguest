"""
Модуль для автоматического определения ID медиа-устройств по имени.
Поддерживает поиск устройств по частичному совпадению имени.
"""
import logging
import subprocess
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MediaDevice:
    """Класс для представления медиа-устройства."""
    device_id: str
    label: str
    kind: str  # 'videoinput' или 'audioinput'
    group_id: str


class DeviceManager:
    """Менеджер для работы с медиа-устройствами."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._devices_cache: Optional[List[MediaDevice]] = None
    
    def get_all_devices(self) -> List[MediaDevice]:
        """
        Получает список всех доступных медиа-устройств.
        
        Returns:
            Список объектов MediaDevice
        """
        if self._devices_cache is not None:
            return self._devices_cache
            
        try:
            # Используем PowerShell для получения информации об устройствах
            devices = self._get_devices_via_powershell()
            self._devices_cache = devices
            self.logger.info(f"Найдено {len(devices)} медиа-устройств")
            return devices
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка устройств: {e}")
            return []
    
    def _get_devices_via_powershell(self) -> List[MediaDevice]:
        """
        Получает список устройств через PowerShell и WMI.
        
        Returns:
            Список объектов MediaDevice
        """
        devices = []
        
        try:
            # Получаем видеоустройства
            video_devices = self._get_video_devices()
            devices.extend(video_devices)
            
            # Получаем аудиоустройства
            audio_devices = self._get_audio_devices()
            devices.extend(audio_devices)
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении устройств через PowerShell: {e}")
            
        return devices
    
    def _get_video_devices(self) -> List[MediaDevice]:
        """Получает список видеоустройств."""
        devices = []
        
        try:
            # PowerShell команда для получения видеоустройств
            ps_command = """
            Get-WmiObject -Class Win32_PnPEntity | Where-Object {
                ($_.PNPClass -eq 'Camera' -or 
                 $_.PNPClass -eq 'Image' -or
                 $_.Name -like '*camera*' -or
                 $_.Name -like '*webcam*' -or
                 $_.Name -like '*video*') -and
                $_.Name -notlike '*microphone*' -and
                $_.Name -notlike '*audio*'
            } | Select-Object Name, DeviceID | ConvertTo-Json
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                device_data = json.loads(result.stdout)
                if isinstance(device_data, dict):
                    device_data = [device_data]
                
                for device in device_data:
                    if device.get('Name'):
                        # Генерируем уникальный ID на основе DeviceID
                        device_id = self._generate_device_id(device.get('DeviceID', ''))
                        devices.append(MediaDevice(
                            device_id=device_id,
                            label=device['Name'],
                            kind='videoinput',
                            group_id=device_id  # Используем device_id как group_id
                        ))
                        
        except Exception as e:
            self.logger.warning(f"Не удалось получить видеоустройства через PowerShell: {e}")
            
        return devices
    
    def _get_audio_devices(self) -> List[MediaDevice]:
        """Получает список аудиоустройств."""
        devices = []
        
        try:
            # PowerShell команда для получения аудиоустройств (включая микрофоны из PnP)
            ps_command = """
            $audioDevices = @()
            
            # Получаем звуковые устройства
            $soundDevices = Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, DeviceID
            foreach ($device in $soundDevices) {
                $audioDevices += @{
                    Name = $device.Name
                    DeviceID = $device.DeviceID
                }
            }
            
            # Получаем микрофоны из PnP устройств
            $micDevices = Get-WmiObject -Class Win32_PnPEntity | Where-Object {
                $_.Name -like '*microphone*' -or
                $_.Name -like '*mic*' -or
                ($_.PNPClass -eq 'AudioEndpoint' -and $_.Name -like '*input*')
            } | Select-Object Name, DeviceID
            
            foreach ($device in $micDevices) {
                $audioDevices += @{
                    Name = $device.Name
                    DeviceID = $device.DeviceID
                }
            }
            
            $audioDevices | ConvertTo-Json
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                device_data = json.loads(result.stdout)
                if isinstance(device_data, dict):
                    device_data = [device_data]
                
                for device in device_data:
                    if device.get('Name'):
                        # Генерируем уникальный ID на основе DeviceID
                        device_id = self._generate_device_id(device.get('DeviceID', ''))
                        devices.append(MediaDevice(
                            device_id=device_id,
                            label=device['Name'],
                            kind='audioinput',
                            group_id=device_id
                        ))
                        
        except Exception as e:
            self.logger.warning(f"Не удалось получить аудиоустройства через PowerShell: {e}")
            
        return devices
    
    def _generate_device_id(self, device_id: str) -> str:
        """
        Генерирует уникальный ID устройства на основе DeviceID.
        Для совместимости с браузером используем упрощенный подход.
        
        Args:
            device_id: DeviceID из WMI
            
        Returns:
            Уникальный ID устройства
        """
        import hashlib
        
        # Создаем более короткий и стабильный ID
        hash_obj = hashlib.md5(device_id.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def find_device_by_name(self, device_name: str, device_type: str = None) -> Optional[MediaDevice]:
        """
        Находит устройство по частичному совпадению имени.
        
        Args:
            device_name: Имя устройства для поиска (например, "Logi")
            device_type: Тип устройства ('videoinput' или 'audioinput'), если None - ищет в обоих типах
            
        Returns:
            Найденное устройство или None
        """
        devices = self.get_all_devices()
        
        if not devices:
            self.logger.warning("Список устройств пуст")
            return None
        
        # Фильтруем по типу устройства если указан
        if device_type:
            devices = [d for d in devices if d.kind == device_type]
        
        # Ищем устройство по частичному совпадению имени (без учета регистра)
        device_name_lower = device_name.lower()
        
        for device in devices:
            if device_name_lower in device.label.lower():
                self.logger.info(f"Найдено устройство: {device.label} (ID: {device.device_id[:20]}...)")
                return device
        
        self.logger.warning(f"Устройство с именем '{device_name}' не найдено")
        return None
    
    def find_video_device_by_name(self, device_name: str) -> Optional[MediaDevice]:
        """
        Находит видеоустройство по имени.
        
        Args:
            device_name: Имя устройства для поиска
            
        Returns:
            Найденное видеоустройство или None
        """
        return self.find_device_by_name(device_name, 'videoinput')
    
    def find_audio_device_by_name(self, device_name: str) -> Optional[MediaDevice]:
        """
        Находит аудиоустройство по имени.
        
        Args:
            device_name: Имя устройства для поиска
            
        Returns:
            Найденное аудиоустройство или None
        """
        return self.find_device_by_name(device_name, 'audioinput')
    
    def get_device_id_by_name(self, device_name: str, device_type: str = None) -> Optional[str]:
        """
        Получает ID устройства по имени.
        
        Args:
            device_name: Имя устройства для поиска
            device_type: Тип устройства ('videoinput' или 'audioinput')
            
        Returns:
            ID устройства или None
        """
        device = self.find_device_by_name(device_name, device_type)
        return device.device_id if device else None
    
    def list_devices(self) -> None:
        """Выводит список всех доступных устройств."""
        devices = self.get_all_devices()
        
        if not devices:
            print("Медиа-устройства не найдены")
            return
        
        print("\n" + "="*60)
        print("ДОСТУПНЫЕ МЕДИА-УСТРОЙСТВА")
        print("="*60)
        
        video_devices = [d for d in devices if d.kind == 'videoinput']
        audio_devices = [d for d in devices if d.kind == 'audioinput']
        
        if video_devices:
            print(f"\n📹 ВИДЕОУСТРОЙСТВА ({len(video_devices)}):")
            for i, device in enumerate(video_devices, 1):
                print(f"  {i}. {device.label}")
                print(f"     ID: {device.device_id[:30]}...")
        
        if audio_devices:
            print(f"\n🎤 АУДИОУСТРОЙСТВА ({len(audio_devices)}):")
            for i, device in enumerate(audio_devices, 1):
                print(f"  {i}. {device.label}")
                print(f"     ID: {device.device_id[:30]}...")
        
        print("="*60 + "\n")
    
    def clear_cache(self) -> None:
        """Очищает кэш устройств."""
        self._devices_cache = None
        self.logger.debug("Кэш устройств очищен")


# Глобальный экземпляр менеджера устройств
device_manager = DeviceManager()
