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

    def get_current_video_codec_from_stats(self):
        script = """
        const stats = [];
        const peers = window.peers;
        if (peers && peers.length > 0) {
            const peer = peers[0];
            const pc = peer.pc;

            return pc.getStats(null).then(stats => {
                const videoCodecs = {
                    outbound: null,
                    inbound: null
                };
                stats.forEach(report => {
                    if (report.type === 'outbound-rtp' && report.kind === 'video') {
                        videoCodecs.outbound = report.codecId; // Кодек для отправляемого видео
                    }
                    if (report.type === 'remote-inbound-rtp' && report.kind === 'video') {
                        videoCodecs.inbound = report.codecId; // Кодек для принимаемого видео
                    }
                });
                return videoCodecs;
            });
        }
        return 'No peers found';
        """
        return self.driver.execute_script(script)

    def get_current_video_frame_rate(self):
        script = """
        const peers = window.peers;
        if (peers && peers.length > 0) {
            const peer = peers[0];
            const pc = peer.pc;

            return pc.getStats(null).then(stats => {
                let frameRate = null;
                stats.forEach(report => {
                    if (report.type === 'outbound-rtp' && report.kind === 'video') {
                        frameRate = report.framesPerSecond; // Получаем частоту кадров
                    }
                });
                return frameRate;
            });
        }
        return 'No peers found';
        """
        return self.driver.execute_script(script)

    def get_video_frame_dimensions(self):
        script = """
        const peers = window.peers;
        if (peers && peers.length > 0) {
            const peer = peers[0];
            const pc = peer.pc;

            return pc.getStats(null).then(stats => {
                let frameDimensions = null;

                stats.forEach(report => {
                    // Ищем данные для исходящего видеопотока
                    if (report.type === 'outbound-rtp' && report.kind === 'video') {
                        const width = report.frameWidth || null; // Ширина исходящего видео
                        const height = report.frameHeight || null; // Высота исходящего видео
                        if (width && height) {
                            frameDimensions = `${width}x${height}`; // Форматируем размеры
                        }
                    }
                });

                return frameDimensions || 'No dimensions found'; // Возвращаем размеры или сообщение об отсутствии
            });
        }
        return 'No peers found'; // Если пиры не найдены
        """
        return self.driver.execute_script(script)
