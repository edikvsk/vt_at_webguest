import subprocess
import time

import psutil
import win32con
import win32gui
import win32process

from utils.logger_config import setup_logger


class ProcessManager:
    def __init__(self, process_path, process_name):
        self.process_path = process_path
        self.process_name = process_name
        self.logger = setup_logger(self.process_name)

    def is_process_running(self):
        """Проверяет, запущен ли процесс с заданным именем."""
        for proc in psutil.process_iter(attrs=['name']):
            if proc.info['name'].lower() == self.process_name.lower():
                return proc  # Возвращаем объект процесса
        return None

    def start_process(self):
        """Запускает процесс, если он не запущен."""
        if not self.is_process_running():
            try:
                subprocess.Popen(self.process_path)  # Запускаем процесс напрямую
                time.sleep(15)  # Задержка для ожидания запуска процесса
                self.logger.info(f"{self.process_name} был запущен.")
            except Exception as e:
                self.logger.error(f"Ошибка при запуске процесса: {e}")
                raise  # Поднимаем исключение, чтобы остановить тест
        else:
            self.logger.info(f"{self.process_name} уже запущен. Процесс не будет запущен.")

    def kill_process(self):
        """Завершает дерево процессов с заданным именем."""
        process = self.is_process_running()
        if process:
            try:
                # Функция для отправки сообщения WM_CLOSE
                def close_process(proc):
                    hwnd = self.get_window_handle(proc.pid)
                    if hwnd:
                        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    else:
                        proc.terminate()  # Если окна нет, принудительно завершаем

                # Попытка закрыть дочерние процессы
                for child in process.children(recursive=True):
                    close_process(child)

                # Попытка закрыть основной процесс
                close_process(process)

                process.wait()  # Ждем завершения процесса
                self.logger.info(f"Процесс '{self.process_name}' и его дочерние процессы завершены.")
            except psutil.NoSuchProcess:
                self.logger.info("Процесс уже завершен.")
            except psutil.AccessDenied:
                self.logger.warning("Нет доступа для завершения процесса.")
            except Exception as e:
                self.logger.error(f"Ошибка при завершении процесса: {e}")
        else:
            self.logger.info(f"Процесс '{self.process_name}' не найден.")

    def get_window_handle(self, pid):
        """Возвращает дескриптор окна для процесса по его PID."""

        def enum_windows(hwnd, pid):
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    handles.append(hwnd)

        handles = []
        win32gui.EnumWindows(enum_windows, pid)
        return handles[0] if handles else None

    def start_monitoring_video_bitrate(self):
        script = """
        return new Promise((resolve, reject) => {
            const peers = window.peers;
            if (!peers || peers.length === 0) {
                return reject('No peers found');
            }

            const pc = peers[0].pc;
            const videoBitrateValues = [];
            const monitoringDuration = 15; // seconds
            const intervalDuration = 1000; // milliseconds

            let previousVideoBytesSent = 0;
            let previousTimestamp = null;
            let intervalCount = 0;
            let maxVideoBitrate = 0;

            const intervalId = setInterval(() => {
                pc.getStats(null).then(stats => {
                    stats.forEach(report => {
                        if (report.type === 'outbound-rtp' && report.kind === 'video') {
                            const currentBytesSent = report.bytesSent;
                            const currentTimestamp = report.timestamp;

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
                            previousTimestamp = currentTimestamp;
                        }
                    });
                }).catch(error => console.error('Error getting stats:', error));

                if (++intervalCount >= monitoringDuration) {
                    clearInterval(intervalId);
                    const averageVideoBitrate = videoBitrateValues.length > 0 
                        ? videoBitrateValues.reduce((a, b) => a + b, 0) / videoBitrateValues.length 
                        : 0;
                    resolve({
                        averageVideo: (averageVideoBitrate / 1e6).toFixed(2), // in Mb/s
                        maxVideo: (maxVideoBitrate / 1e6).toFixed(2) // in Mb/s
                    });
                }
            }, intervalDuration);
        });
        """

        result = self.driver.execute_script(script)
        return result
