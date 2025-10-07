#Requires -Version 5.1

param(
    [string]$InstallRoot = "$PSScriptRoot/../.tools",
    [string]$Channel = "beta", # chrome channel: stable|beta|dev|canary (windows)
    [int]$MaxRetries = 3,
    [int]$RetryDelaySec = 5,
    [int]$TimeoutSec = 900
)

$ErrorActionPreference = "Stop"

Write-Host "[Chrome Setup] Channel: $Channel" -ForegroundColor Cyan

# Normalize channel (API uses 'Stable'|'Beta'|'Dev'|'Canary')
switch -Regex ($Channel.ToLower()) {
    '^stable$' { $Channel = 'Stable'; break }
    '^beta$'   { $Channel = 'Beta'; break }
    '^dev$'    { $Channel = 'Dev'; break }
    '^canary$' { $Channel = 'Canary'; break }
    default    { Write-Warning "Unknown channel '$Channel'. Falling back to 'Beta'"; $Channel = 'Beta' }
}

# Normalize paths
$InstallRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "../.tools"))
$ChromeRoot = Join-Path $InstallRoot "chrome-$Channel"
$DriverRoot = Join-Path $InstallRoot "chromedriver-$Channel"

New-Item -ItemType Directory -Force -Path $ChromeRoot | Out-Null
New-Item -ItemType Directory -Force -Path $DriverRoot | Out-Null

function Get-LastKnownGoodForChannel {
    param([string]$channel)
    $lkUrl = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
    Write-Host "[Chrome Setup] Fetching last-known-good versions..." -ForegroundColor Cyan
    $json = Invoke-RestMethod -UseBasicParsing -Uri $lkUrl
    $node = $json.channels.$channel
    if (-not $node) { throw "No channel node found for '$channel'" }
    return $node
}

function Get-DownloadUrl {
    param(
        [object]$channelNode,
        [string]$product # 'chrome' | 'chromedriver'
    )
    $platform = "win64"  # on Windows x64
    $downloads = $channelNode.downloads.$product | Where-Object { $_.platform -eq $platform }
    if (-not $downloads) { throw "No $product downloads for $platform on channel node" }
    return $downloads[0].url
}

function Download-File {
    param(
        [string]$Url,
        [string]$OutFile
    )
    for ($i = 1; $i -le $MaxRetries; $i++) {
        try {
            Write-Host "[Download] ($i/$MaxRetries) $Url" -ForegroundColor Cyan
            # Try BITS first for robust downloading with progress
            if (Get-Command Start-BitsTransfer -ErrorAction SilentlyContinue) {
                Start-BitsTransfer -Source $Url -Destination $OutFile -DisplayName "ChromeForTesting" -Description "Downloading" -ErrorAction Stop
            } else {
                Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $OutFile -TimeoutSec $TimeoutSec -ErrorAction Stop
            }
            if ((Test-Path $OutFile) -and ((Get-Item $OutFile).Length -gt 0)) {
                return
            } else {
                throw "Empty or missing file after download"
            }
        } catch {
            Write-Warning "[Download] Failed: $($_.Exception.Message)"
            if ($i -lt $MaxRetries) {
                Start-Sleep -Seconds $RetryDelaySec
            } else {
                throw
            }
        }
    }
}

function Expand-ZipTo {
    param([string]$zipPath, [string]$dest)
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipPath, $dest)
}

$node = Get-LastKnownGoodForChannel -channel $Channel
$chromeUrl = Get-DownloadUrl -channelNode $node -product "chrome"
$driverUrl = Get-DownloadUrl -channelNode $node -product "chromedriver"

Write-Host "[Chrome Setup] Version: $($node.version)" -ForegroundColor Green

$tmp = New-Item -ItemType Directory -Force -Path (Join-Path $InstallRoot "tmp")
$chromeZip = Join-Path $tmp.FullName "chrome.zip"
$driverZip = Join-Path $tmp.FullName "chromedriver.zip"

# Skip download if already installed (both exes exist)
$existingChrome = Get-ChildItem -Recurse -Path $ChromeRoot -Filter chrome.exe -ErrorAction SilentlyContinue | Select-Object -First 1
$existingDriver = Get-ChildItem -Recurse -Path $DriverRoot -Filter chromedriver.exe -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existingChrome -and $existingDriver) {
    Write-Host "[Chrome Setup] Existing installation detected. Skipping download." -ForegroundColor Yellow
} else {
    Write-Host "[Chrome Setup] Downloading Chrome..." -ForegroundColor Cyan
    Download-File -Url $chromeUrl -OutFile $chromeZip
    Write-Host "[Chrome Setup] Downloading Chromedriver..." -ForegroundColor Cyan
    Download-File -Url $driverUrl -OutFile $driverZip
}

Write-Host "[Chrome Setup] Extracting..." -ForegroundColor Cyan
if (Test-Path $chromeZip) { Expand-ZipTo -zipPath $chromeZip -dest $ChromeRoot }
if (Test-Path $driverZip) { Expand-ZipTo -zipPath $driverZip -dest $DriverRoot }

# chrome for testing structure: chrome-win64/chrome.exe, chromedriver-win64/chromedriver.exe
$chromeExe = Get-ChildItem -Recurse -Path $ChromeRoot -Filter chrome.exe | Select-Object -First 1
$driverExe = Get-ChildItem -Recurse -Path $DriverRoot -Filter chromedriver.exe | Select-Object -First 1

if (-not $chromeExe -or -not $driverExe) { throw "Failed to locate chrome.exe or chromedriver.exe after extraction" }

$envFile = Join-Path $InstallRoot ".env.browser.ps1"
$envLines = @(
    "# Auto-generated by install_chrome_beta.ps1",
    "# Version: $($node.version) Channel: $Channel",
    ('$env:CHROME_BROWSER_PATH = "{0}"' -f $chromeExe.FullName),
    ('$env:CHROME_DRIVER_PATH = "{0}"' -f $driverExe.FullName)
)
$envLines | Set-Content -Encoding UTF8 -Path $envFile

Write-Host "[Chrome Setup] Paths:" -ForegroundColor Yellow
Write-Host " CHROME_BROWSER_PATH = $($chromeExe.FullName)"
Write-Host " CHROME_DRIVER_PATH = $($driverExe.FullName)"
Write-Host "[Chrome Setup] To load paths in current session: . `"$envFile`"" -ForegroundColor Yellow

# Also set for current process so subsequent commands in this session see them
$env:CHROME_BROWSER_PATH = $chromeExe.FullName
$env:CHROME_DRIVER_PATH = $driverExe.FullName

Write-Host "[Chrome Setup] Done." -ForegroundColor Green


