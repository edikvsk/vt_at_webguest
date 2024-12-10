import time

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

    def get_video_frame_rate(self):
        script = """
        const peers = window.peers;
        if (peers && peers.length > 0) {
            const peer = peers[0];
            const pc = peer.pc;

            return pc.getStats(null).then(stats => {
                let frameCount = 0;
                stats.forEach(report => {
                    if (report.type === 'outbound-rtp' && report.kind === 'video') {
                        frameCount = report.framesEncoded; // Получаем общее количество закодированных кадров
                    }
                });
                return frameCount;
            });
        }
        return 'No peers found';
        """

        # Ожидаем, пока peers не будут доступны
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return window.peers && window.peers.length > 0;")
        )

        # Получаем количество кадров в начале замера
        initial_frame_count = self.driver.execute_script(script)

        # Ждем 3 секунды
        time.sleep(3)

        # Получаем количество кадров снова
        final_frame_count = self.driver.execute_script(script)

        # Вычисляем количество кадров, полученных за 3 секунды
        if isinstance(initial_frame_count, (int, float)) and isinstance(final_frame_count, (int, float)):
            frames_in_3_seconds = final_frame_count - initial_frame_count

            # Вычисляем среднюю частоту кадров в секунду
            average_frame_rate = frames_in_3_seconds / 3.0

            # Возвращаем соответствующее текстовое значение
            if 12 <= average_frame_rate < 18:
                return "15 FPS"
            elif 27 <= average_frame_rate < 33:
                return "30 FPS"
            elif 57 <= average_frame_rate < 63:
                return "60 FPS"
            else:
                return f"{average_frame_rate:.2f} FPS"  # Возвращаем значение FPS с двумя знаками после запятой
        else:
            return initial_frame_count  # Возвращаем сообщение, если нет доступных peers

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
                            frameDimensions = `${width}X${height}`; // Форматируем размеры
                        }
                    }
                });

                return frameDimensions || 'No dimensions found'; // Возвращаем размеры или сообщение об отсутствии
            });
        }
        return 'No peers found'; // Если пиры не найдены
        """

        # Ожидаем, пока peers не будут доступны
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return window.peers && window.peers.length > 0;")
        )

        return self.driver.execute_script(script)

    def start_monitoring_bitrate(self):
        script = """
        return new Promise((resolve, reject) => {
            const peers = window.peers;
            if (!peers || peers.length === 0) {
                return reject('No peers found');
            }

            const pc = peers[0].pc;
            const videoBitrateValues = [];
            const audioBitrateValues = [];
            const monitoringDuration = 15; // seconds
            const intervalDuration = 1000; // milliseconds

            let previousVideoBytesSent = 0;
            let previousAudioBytesSent = 0;
            let previousTimestamp = null;
            let intervalCount = 0;
            let maxVideoBitrate = 0;
            let maxAudioBitrate = 0;

            const intervalId = setInterval(() => {
                pc.getStats(null).then(stats => {
                    stats.forEach(report => {
                        if (report.type === 'outbound-rtp') {
                            const currentBytesSent = report.bytesSent;
                            const currentTimestamp = report.timestamp;

                            if (report.kind === 'video') {
                                if (previousTimestamp !== null) {
                                    const bytesDifference = currentBytesSent - previousVideoBytesSent;
                                    const timeDifference = (currentTimestamp - previousTimestamp) / 1000;

                                    if (bytesDifference > 0 && timeDifference > 0) {
                                        const videoBitrate = (bytesDifference * 8) / timeDifference; // in bits per second
                                        videoBitrateValues.push(videoBitrate);
                                        if (videoBitrate > maxVideoBitrate) {
                                            maxVideoBitrate = videoBitrate;
                                        }
                                    }
                                }
                                previousVideoBytesSent = currentBytesSent;
                            } else if (report.kind === 'audio') {
                                if (previousTimestamp !== null) {
                                    const bytesDifference = currentBytesSent - previousAudioBytesSent;
                                    const timeDifference = (currentTimestamp - previousTimestamp) / 1000;

                                    if (bytesDifference > 0 && timeDifference > 0) {
                                        const audioBitrate = (bytesDifference * 8) / timeDifference; // in bits per second
                                        audioBitrateValues.push(audioBitrate);
                                        if (audioBitrate > maxAudioBitrate) {
                                            maxAudioBitrate = audioBitrate;
                                        }
                                    }
                                }
                                previousAudioBytesSent = currentBytesSent;
                            }
                            previousTimestamp = currentTimestamp;
                        }
                    });
                }).catch(error => console.error('Error getting stats:', error));

                if (++intervalCount >= monitoringDuration) {
                    clearInterval(intervalId);
                    const averageVideoBitrate = videoBitrateValues.length > 0 
                        ? videoBitrateValues.reduce((a, b) => a + b, 0) / videoBitrateValues.length 
                        : 0;
                    const averageAudioBitrate = audioBitrateValues.length > 0 
                        ? audioBitrateValues.reduce((a, b) => a + b, 0) / audioBitrateValues.length 
                    : 0;

                resolve({
                    averageVideo: (averageVideoBitrate / 1e6).toFixed(2), // in Mb/s
                    maxVideo: (maxVideoBitrate / 1e6).toFixed(2), // in Mb/s
                    averageAudio: (averageAudioBitrate / 1e3).toFixed(2), // in kb/s
                    maxAudio: (maxAudioBitrate / 1e3).toFixed(2) // in kb/s
                });
            }
        }, intervalDuration);
    });
    """

        result = self.driver.execute_script(script)
        return result

    @staticmethod
    def format_audio_bitrate(max_audio_bitrate):
        max_audio_bitrate = float(max_audio_bitrate)
        if 4 <= max_audio_bitrate < 8:
            return "AUDIO BITRATE\n6K"
        elif 8 <= max_audio_bitrate < 14:
            return "AUDIO BITRATE\n10K"
        elif 18 <= max_audio_bitrate < 25:
            return "AUDIO BITRATE\n20K"
        elif 36 <= max_audio_bitrate < 46:
            return "AUDIO BITRATE\n40K"
        elif 90 <= max_audio_bitrate < 104:
            return "AUDIO BITRATE\n96K"
        elif 180 <= max_audio_bitrate < 205:
            return "AUDIO BITRATE\n192K"
        elif 490 <= max_audio_bitrate < 530:
            return "AUDIO BITRATE\n510K"
        else:
            return f"AUDIO BITRATE {max_audio_bitrate}K"  # для значений вне указанных диапазонов
