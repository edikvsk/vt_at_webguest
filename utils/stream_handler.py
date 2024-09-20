from selenium.webdriver.support.ui import WebDriverWait


class StreamHandler:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_webrtc_connection(self, timeout=10):
        """Ожидает подключения WebRTC стрима в течение заданного времени."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: self.is_webrtc_connected()
            )
            return True
        except Exception as e:
            raise Exception("WebRTC стрим не запущен.") from e

    def is_webrtc_connected(self):
        """Проверяет, подключен ли WebRTC стрим."""
        script = """
        var videoElement = document.querySelector('video[data-cy="remote-video"]');
        return (videoElement && videoElement.srcObject !== null);
        """
        return self.driver.execute_script(script)

    def is_audio_stream_active(self):
        script = """
        var videoElement = document.querySelector('video[data-cy="remote-video"]');
        return (videoElement && videoElement.srcObject !== null &&
                videoElement.srcObject.getAudioTracks().length > 0);
        """
        return self.driver.execute_script(script)

    def is_video_stream_active(self):
        script = """
        var videoElement = document.querySelector('video[data-cy="remote-video"]');
        return (videoElement && videoElement.srcObject !== null &&
                videoElement.srcObject.getVideoTracks().length > 0);
        """
        return self.driver.execute_script(script)
