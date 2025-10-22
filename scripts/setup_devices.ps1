# PowerShell скрипт для настройки переменных окружения для медиа-устройств
# Использование: .\scripts\setup_devices.ps1 -CameraName "Logi" -MicName "Logi"

param(
    [string]$CameraName = "Logi",
    [string]$MicName = "Logi",
    [string]$VideoDeviceId = "",
    [string]$AudioDeviceId = ""
)

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "НАСТРОЙКА МЕДИА-УСТРОЙСТВ ДЛЯ VT WEBGUEST" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Устанавливаем переменные окружения для текущей сессии
Write-Host "`nУстанавливаем переменные окружения:" -ForegroundColor Yellow

if ($VideoDeviceId) {
    $env:VIDEO_DEVICE_ID = $VideoDeviceId
    Write-Host "  VIDEO_DEVICE_ID = $VideoDeviceId" -ForegroundColor Green
} else {
    $env:CAMERA_FOR_SELECTION = $CameraName
    Write-Host "  CAMERA_FOR_SELECTION = $CameraName" -ForegroundColor Green
}

if ($AudioDeviceId) {
    $env:AUDIO_DEVICE_ID = $AudioDeviceId
    Write-Host "  AUDIO_DEVICE_ID = $AudioDeviceId" -ForegroundColor Green
} else {
    $env:MIC_FOR_SELECTION = $MicName
    Write-Host "  MIC_FOR_SELECTION = $MicName" -ForegroundColor Green
}

Write-Host "`nТестируем конфигурацию..." -ForegroundColor Yellow

# Запускаем тест устройств
try {
    python scripts\test_devices.py
    Write-Host "`n✓ Тест устройств выполнен успешно" -ForegroundColor Green
} catch {
    Write-Host "`n✗ Ошибка при тестировании устройств: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host "НАСТРОЙКА ЗАВЕРШЕНА" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

Write-Host "`nДля постоянного сохранения переменных окружения добавьте их в профиль PowerShell:" -ForegroundColor Yellow
Write-Host "  [Environment]::SetEnvironmentVariable('CAMERA_FOR_SELECTION', '$CameraName', 'User')" -ForegroundColor Gray
Write-Host "  [Environment]::SetEnvironmentVariable('MIC_FOR_SELECTION', '$MicName', 'User')" -ForegroundColor Gray

Write-Host "`nИли создайте файл .env в корне проекта с содержимым:" -ForegroundColor Yellow
Write-Host "  CAMERA_FOR_SELECTION=$CameraName" -ForegroundColor Gray
Write-Host "  MIC_FOR_SELECTION=$MicName" -ForegroundColor Gray
