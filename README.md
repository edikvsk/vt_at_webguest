1. pip install selenium
2. pip install pytest
3. pip install psutil
4. pip install pyperclip
5. По пути \vt_at_webguest\utils\config.py изменить значение переменной CHROME_DRIVER_PATH = "<Путь к Chromedriver>"
6. По пути \vt_at_webguest\utils\config.py изменить значение переменной PROCESS_PATH = "<Путь к исполняемому файлу VT>"
7. По пути \vt_at_webguest\utils\config.py изменить значение переменной CHROME_BROWSER_PATH = "<Путь к Chrome Browser>"
8. По пути \vt_at_webguest\utils\config.py изменить значение переменной CONFIG_INI = "<\vt_at_webguest\utils\>"
9. По пути \vt_at_webguest\utils\config.py изменить значение переменной SOURCE_TO_PUBLISHING = "<Наименование источника
   для паблишинга>"
10. По пути \vt_at_webguest\utils\config.py изменить значение переменных VIDEO_DEVICE_ID/AUDIO_DEVICE_ID ->
    --> Необходимо указать идентификаторы устройств ввода аудио/видео.
    --> Алгоритм получения идентификаторов:
    1. Запустить веб гест стрим
    2. В Chrome DevTools консоли ввести скрипт:
       navigator.mediaDevices.enumerateDevices()
       .then(devices => {
       devices.forEach(device => {
       if (device.kind === 'videoinput') {
       console.log('Video Device ID:', device.deviceId, 'Label:', device.label);
       } else if (device.kind === 'audioinput') {
       console.log('Audio Device ID:', device.deviceId, 'Label:', device.label);
       }
       });
       })
       .catch(err => {
       console.error('Error accessing media devices.', err);
       });
    3. По наименованию видео/аудио девайса скопировать требуемый идентификатор

11. По пути \vt_at_webguest\utils\config.py изменить значение переменной CAMERA_FOR_SELECTION_IN_TEST_CAMERA_SELECT -
    на наименование веб камеры
12. По пути \vt_at_webguest\utils\config.py изменить значение переменной MIC_FOR_SELECTION_IN_TEST_MICROPHONE_SELECT -
    на наименование микрофона