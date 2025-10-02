"""
Централизованное управление тестовыми данными для автотестов VT WebGuest.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class Resolution(Enum):
    """Поддерживаемые разрешения."""
    HD_720P = "1280 × 720"
    FULL_HD = "1920 × 1080" 
    SD_480P = "640 × 480"
    SD_360P = "640 × 360"
    QVGA = "320 × 240"


class FrameRate(Enum):
    """Поддерживаемые частоты кадров."""
    FPS_15 = "15 FPS"
    FPS_30 = "30 FPS" 
    FPS_60 = "60 FPS"


class AudioBitrate(Enum):
    """Поддерживаемые битрейты аудио."""
    BITRATE_6K = "AUDIO BITRATE\n6K"
    BITRATE_10K = "AUDIO BITRATE\n10K"
    BITRATE_20K = "AUDIO BITRATE\n20K"
    BITRATE_40K = "AUDIO BITRATE\n40K"
    BITRATE_96K = "AUDIO BITRATE\n96K"
    BITRATE_192K = "AUDIO BITRATE\n192K"
    BITRATE_510K = "AUDIO BITRATE\n510K"


class VideoBitrate(Enum):
    """Поддерживаемые битрейты видео."""
    BITRATE_0_5M = "VIDEO BITRATE\n0.5M"
    BITRATE_0_75M = "VIDEO BITRATE\n0.75M"
    BITRATE_1M = "VIDEO BITRATE\n1.0M"
    BITRATE_1_5M = "VIDEO BITRATE\n1.5M"
    BITRATE_2_5M = "VIDEO BITRATE\n2.5M"
    BITRATE_5M = "VIDEO BITRATE\n5M"
    BITRATE_7_5M = "VIDEO BITRATE\n7.5M"
    BITRATE_10M = "VIDEO BITRATE\n10M"
    BITRATE_12_5M = "VIDEO BITRATE\n12.5M"
    BITRATE_15M = "VIDEO BITRATE\n15M"
    BITRATE_20M = "VIDEO BITRATE\n20M"


class VideoEncoder(Enum):
    """Поддерживаемые видеокодеки."""
    H264 = "H.264"
    H265 = "H.265"


class AudioChannels(Enum):
    """Поддерживаемые аудиоканалы."""
    MONO = "MONO"
    STEREO = "STEREO"


@dataclass
class UserCredentials:
    """Данные пользователя для авторизации."""
    name: str
    location: str = ""
    login: str = ""
    password: str = ""


@dataclass
class StreamSettings:
    """Настройки стрима."""
    resolution: Resolution = Resolution.HD_720P
    framerate: FrameRate = FrameRate.FPS_30
    audio_bitrate: AudioBitrate = AudioBitrate.BITRATE_96K
    video_bitrate: VideoBitrate = VideoBitrate.BITRATE_2_5M
    video_encoder: VideoEncoder = VideoEncoder.H264
    audio_channels: AudioChannels = AudioChannels.STEREO
    mirroring_enabled: bool = False
    audio_enhancements_enabled: bool = False


@dataclass
class TestScenario:
    """Сценарий теста."""
    name: str
    description: str
    user_credentials: UserCredentials
    stream_settings: Optional[StreamSettings] = None
    expected_result: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TestDataProvider:
    """Провайдер тестовых данных."""
    
    @staticmethod
    def get_valid_user_credentials() -> List[UserCredentials]:
        """Возвращает список валидных учетных данных пользователей."""
        return [
            UserCredentials(name="TestUser1", location="Moscow"),
            UserCredentials(name="TestUser2", location="Saint Petersburg"),
            UserCredentials(name="Тестовый Пользователь", location="Москва"),
            UserCredentials(name="User_123", location="Test Location"),
        ]
    
    @staticmethod
    def get_invalid_user_credentials() -> List[UserCredentials]:
        """Возвращает список невалидных учетных данных."""
        return [
            UserCredentials(name="", location="Moscow"),  # Пустое имя
            UserCredentials(name="TestUser", location=""),  # Пустая локация
            UserCredentials(name="", location=""),  # Пустые поля
            UserCredentials(name="a" * 256, location="Moscow"),  # Слишком длинное имя
            UserCredentials(name="TestUser", location="b" * 256),  # Слишком длинная локация
        ]
    
    @staticmethod
    def get_security_credentials() -> List[UserCredentials]:
        """Возвращает учетные данные для тестов безопасности."""
        return [
            UserCredentials(
                name="SecurityUser1", 
                location="Secure Location",
                login="admin",
                password="password123"
            ),
            UserCredentials(
                name="SecurityUser2",
                location="Test Location", 
                login="user",
                password="userpass"
            ),
        ]
    
    @staticmethod
    def get_stream_settings_combinations() -> List[StreamSettings]:
        """Возвращает различные комбинации настроек стрима."""
        return [
            # Стандартные настройки
            StreamSettings(),
            
            # Высокое качество
            StreamSettings(
                resolution=Resolution.FULL_HD,
                framerate=FrameRate.FPS_60,
                video_bitrate=VideoBitrate.BITRATE_15M,
                audio_bitrate=AudioBitrate.BITRATE_192K
            ),
            
            # Низкое качество
            StreamSettings(
                resolution=Resolution.QVGA,
                framerate=FrameRate.FPS_15,
                video_bitrate=VideoBitrate.BITRATE_0_5M,
                audio_bitrate=AudioBitrate.BITRATE_6K
            ),
            
            # С включенными дополнительными опциями
            StreamSettings(
                resolution=Resolution.HD_720P,
                framerate=FrameRate.FPS_30,
                mirroring_enabled=True,
                audio_enhancements_enabled=True,
                audio_channels=AudioChannels.MONO
            ),
        ]
    
    @staticmethod
    def get_resolution_test_data() -> List[Dict[str, Any]]:
        """Возвращает тестовые данные для проверки разрешений."""
        return [
            {
                "resolution": Resolution.HD_720P,
                "expected_dimensions": "1280X720",
                "description": "HD 720p resolution test"
            },
            {
                "resolution": Resolution.FULL_HD,
                "expected_dimensions": "1920X1080", 
                "description": "Full HD resolution test"
            },
            {
                "resolution": Resolution.SD_480P,
                "expected_dimensions": "640X480",
                "description": "SD 480p resolution test"
            },
            {
                "resolution": Resolution.SD_360P,
                "expected_dimensions": "640X360",
                "description": "SD 360p resolution test"
            },
            {
                "resolution": Resolution.QVGA,
                "expected_dimensions": "320X240",
                "description": "QVGA resolution test"
            },
        ]
    
    @staticmethod
    def get_framerate_test_data() -> List[Dict[str, Any]]:
        """Возвращает тестовые данные для проверки частоты кадров."""
        return [
            {
                "framerate": FrameRate.FPS_15,
                "expected_range": (12, 18),
                "description": "15 FPS test"
            },
            {
                "framerate": FrameRate.FPS_30,
                "expected_range": (27, 33),
                "description": "30 FPS test"
            },
            {
                "framerate": FrameRate.FPS_60,
                "expected_range": (57, 63),
                "description": "60 FPS test"
            },
        ]
    
    @staticmethod
    def get_audio_bitrate_test_data() -> List[Dict[str, Any]]:
        """Возвращает тестовые данные для проверки аудио битрейта."""
        return [
            {
                "bitrate": AudioBitrate.BITRATE_6K,
                "expected_range": (4, 8),
                "description": "6K audio bitrate test"
            },
            {
                "bitrate": AudioBitrate.BITRATE_96K,
                "expected_range": (90, 104),
                "description": "96K audio bitrate test"
            },
            {
                "bitrate": AudioBitrate.BITRATE_192K,
                "expected_range": (180, 205),
                "description": "192K audio bitrate test"
            },
        ]
    
    @staticmethod
    def get_video_bitrate_test_data() -> List[Dict[str, Any]]:
        """Возвращает тестовые данные для проверки видео битрейта."""
        return [
            {
                "bitrate": VideoBitrate.BITRATE_0_5M,
                "expected_range": (0.4, 0.6),
                "description": "0.5M video bitrate test"
            },
            {
                "bitrate": VideoBitrate.BITRATE_2_5M,
                "expected_range": (2.0, 3.0),
                "description": "2.5M video bitrate test"
            },
            {
                "bitrate": VideoBitrate.BITRATE_10M,
                "expected_range": (9.0, 11.0),
                "description": "10M video bitrate test"
            },
        ]
    
    @staticmethod
    def get_negative_test_scenarios() -> List[TestScenario]:
        """Возвращает сценарии негативных тестов."""
        return [
            TestScenario(
                name="login_empty_name",
                description="Попытка входа с пустым именем",
                user_credentials=UserCredentials(name="", location="Moscow"),
                expected_result="Ошибка валидации - Please provide name",
                tags=["negative", "validation", "login"]
            ),
            TestScenario(
                name="login_empty_location",
                description="Попытка входа с пустой локацией",
                user_credentials=UserCredentials(name="TestUser", location=""),
                expected_result="Ошибка валидации - Please provide location",
                tags=["negative", "validation", "login"]
            ),
            TestScenario(
                name="connection_same_name",
                description="Подключение с уже используемым именем",
                user_credentials=UserCredentials(name="ExistingUser", location="Moscow"),
                expected_result="Ошибка подключения - имя уже используется",
                tags=["negative", "connection", "duplicate"]
            ),
        ]
    
    @staticmethod
    def get_smoke_test_scenarios() -> List[TestScenario]:
        """Возвращает сценарии smoke-тестов."""
        return [
            TestScenario(
                name="basic_stream_start",
                description="Базовый запуск стрима",
                user_credentials=UserCredentials(name="SmokeTestUser", location="Test"),
                stream_settings=StreamSettings(),
                expected_result="Стрим успешно запущен",
                tags=["smoke", "stream", "basic"]
            ),
            TestScenario(
                name="settings_change",
                description="Изменение настроек стрима",
                user_credentials=UserCredentials(name="SettingsUser", location="Test"),
                stream_settings=StreamSettings(
                    resolution=Resolution.HD_720P,
                    framerate=FrameRate.FPS_30
                ),
                expected_result="Настройки успешно применены",
                tags=["smoke", "settings", "change"]
            ),
        ]
    
    @staticmethod
    def get_url_test_data() -> List[Dict[str, Any]]:
        """Возвращает тестовые данные для URL параметров."""
        return [
            {
                "parameter": "audio",
                "values": ["0", "1", "f", "false", "t", "true"],
                "description": "Audio parameter test"
            },
            {
                "parameter": "autojoin", 
                "values": ["0", "1"],
                "description": "Autojoin parameter test"
            },
            {
                "parameter": "selfie",
                "values": ["0", "1", "f", "false", "t", "true"],
                "description": "Selfie parameter test"
            },
        ]
    
    @staticmethod
    def get_incorrect_url_data() -> List[str]:
        """Возвращает некорректные URL для тестирования."""
        return [
            "http://invalid-url",
            "https://nonexistent.domain.com",
            "not-a-url-at-all",
            "ftp://wrong.protocol.com",
            "",
            "javascript:alert('xss')",
        ]


# Глобальный экземпляр провайдера данных
test_data = TestDataProvider()
