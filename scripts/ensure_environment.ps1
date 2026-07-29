#Requires -Version 5.1

[CmdletBinding()]
param(
    [string]$PythonVersion = "3.11.9",
    [string]$NuGetSource = "https://api.nuget.org/v3/index.json",
    [string]$NuGetExePath = "",
    [string]$NuGetDownloadUrl = "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe",
    [string]$WheelSource = "",
    [ValidateSet("stable", "beta", "dev", "canary")]
    [string]$ChromeChannel = "beta",
    [switch]$SkipChrome,
    [switch]$Force,
    [switch]$ValidateOnly,
    [int]$LockTimeoutSec = 300
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ToolsRoot = Join-Path $ProjectRoot ".tools"
$VenvRoot = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvRoot "Scripts\python.exe"
$PythonPackagesRoot = Join-Path $ToolsRoot "python-runtime"
$PythonPackageRoot = Join-Path $PythonPackagesRoot "python"
$PackagePython = Join-Path $PythonPackageRoot "tools\python.exe"
$StatePath = Join-Path $ToolsRoot "environment-state.json"
$EnvironmentFile = Join-Path $ToolsRoot ".env.test.ps1"
$BrowserEnvironmentFile = Join-Path $ToolsRoot ".env.browser.ps1"
$LockPath = Join-Path $ToolsRoot ".ensure-environment.lock"

function Write-Step {
    param([string]$Message)
    Write-Host "[Environment] $Message" -ForegroundColor Cyan
}

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [Parameter(Mandatory = $true)]
        [string]$Description
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Description failed with exit code $LASTEXITCODE."
    }
}

function Assert-SafeLocalDirectory {
    param([string]$Path)

    $resolvedRoot = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd("\") + "\"
    $resolvedPath = [System.IO.Path]::GetFullPath($Path).TrimEnd("\") + "\"
    if (-not $resolvedPath.StartsWith(
        $resolvedRoot,
        [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to modify a directory outside the repository: $Path"
    }
}

function Remove-SafeLocalDirectory {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    Assert-SafeLocalDirectory -Path $Path
    Remove-Item -LiteralPath $Path -Recurse -Force
}

function Get-State {
    if (-not (Test-Path -LiteralPath $StatePath -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json
    }
    catch {
        Write-Warning "Ignoring invalid environment state: $($_.Exception.Message)"
        return $null
    }
}

function Get-StateValue {
    param(
        [object]$State,
        [string]$Name
    )

    if ($null -eq $State) {
        return $null
    }

    $property = $State.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }

    return [string]$property.Value
}

function Get-PythonVersion {
    param([string]$PythonExecutable)

    if (-not (Test-Path -LiteralPath $PythonExecutable -PathType Leaf)) {
        return $null
    }

    try {
        $version = & $PythonExecutable -c "import sys; print(sys.version.split()[0])" 2>$null
        if ($LASTEXITCODE -ne 0) {
            return $null
        }
        return ([string]$version).Trim()
    }
    catch {
        return $null
    }
}

function Test-PythonDependencies {
    param(
        [string]$PythonExecutable,
        [switch]$Quiet
    )

    if (-not (Test-Path -LiteralPath $PythonExecutable -PathType Leaf)) {
        return $false
    }

    # Use Python single-quoted strings here. Windows PowerShell 5.1 can strip
    # embedded double quotes while converting a native process argument.
    $probe = "import importlib; modules = ('selenium', 'pytest', 'psutil', 'pyperclip', 'pywinauto', 'win32api'); [importlib.import_module(module) for module in modules]; print('Python dependencies: OK')"

    try {
        if ($Quiet) {
            & $PythonExecutable -c $probe *> $null
        }
        else {
            & $PythonExecutable -c $probe
        }
        if ($LASTEXITCODE -ne 0) {
            return $false
        }

        if ($Quiet) {
            & $PythonExecutable -m pip check *> $null
        }
        else {
            & $PythonExecutable -m pip check
        }
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Test-BrowserEnvironment {
    param([string]$ExpectedChannel)

    if (-not (Test-Path -LiteralPath $BrowserEnvironmentFile -PathType Leaf)) {
        return $false
    }

    $channelPattern = "Channel:\s*" + [regex]::Escape($ExpectedChannel)
    $environmentText = Get-Content -LiteralPath $BrowserEnvironmentFile -Raw
    if ($environmentText -notmatch $channelPattern) {
        return $false
    }

    try {
        . $BrowserEnvironmentFile
    }
    catch {
        return $false
    }

    return (
        -not [string]::IsNullOrWhiteSpace($env:CHROME_BROWSER_PATH) -and
        -not [string]::IsNullOrWhiteSpace($env:CHROME_DRIVER_PATH) -and
        (Test-Path -LiteralPath $env:CHROME_BROWSER_PATH -PathType Leaf) -and
        (Test-Path -LiteralPath $env:CHROME_DRIVER_PATH -PathType Leaf)
    )
}

function Get-NuGetExecutable {
    if (-not [string]::IsNullOrWhiteSpace($NuGetExePath)) {
        $resolved = [System.IO.Path]::GetFullPath($NuGetExePath)
        if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
            throw "NuGet executable was not found: $resolved"
        }
        return $resolved
    }

    $availableNuGet = Get-Command "nuget.exe" -ErrorAction SilentlyContinue
    if ($null -ne $availableNuGet) {
        return $availableNuGet.Source
    }

    $localNuGetDirectory = Join-Path $ToolsRoot "nuget-client"
    $localNuGet = Join-Path $localNuGetDirectory "nuget.exe"
    if (Test-Path -LiteralPath $localNuGet -PathType Leaf) {
        return $localNuGet
    }

    if ($ValidateOnly) {
        throw "NuGet is not available and validation-only mode cannot download it."
    }

    Write-Step "Downloading the NuGet command-line client"
    New-Item -ItemType Directory -Path $localNuGetDirectory -Force | Out-Null
    try {
        [System.Net.ServicePointManager]::SecurityProtocol =
            [System.Net.ServicePointManager]::SecurityProtocol -bor
            [System.Net.SecurityProtocolType]::Tls12
    }
    catch {
        # TLS 1.2 is already the default on newer systems.
    }

    Invoke-WebRequest `
        -UseBasicParsing `
        -Uri $NuGetDownloadUrl `
        -OutFile $localNuGet

    if (-not (Test-Path -LiteralPath $localNuGet -PathType Leaf)) {
        throw "NuGet download did not produce $localNuGet."
    }

    Unblock-File -LiteralPath $localNuGet -ErrorAction SilentlyContinue
    return $localNuGet
}

function Ensure-PackagePython {
    $currentVersion = Get-PythonVersion -PythonExecutable $PackagePython
    if (-not $Force -and $currentVersion -eq $PythonVersion) {
        Write-Step "Packaged Python $currentVersion is ready"
        return
    }

    if ($ValidateOnly) {
        throw "Packaged Python $PythonVersion is not ready at $PackagePython."
    }

    if (Test-Path -LiteralPath $PythonPackageRoot) {
        Write-Step "Replacing packaged Python $currentVersion with $PythonVersion"
        Remove-SafeLocalDirectory -Path $PythonPackageRoot
    }

    $nuget = Get-NuGetExecutable
    New-Item -ItemType Directory -Path $PythonPackagesRoot -Force | Out-Null
    Write-Step "Restoring Python $PythonVersion from NuGet"

    $arguments = @(
        "install",
        "python",
        "-Version", $PythonVersion,
        "-ExcludeVersion",
        "-OutputDirectory", $PythonPackagesRoot,
        "-Source", $NuGetSource,
        "-NonInteractive",
        "-Verbosity", "quiet"
    )
    Invoke-NativeCommand `
        -FilePath $nuget `
        -Arguments $arguments `
        -Description "Python NuGet restore"

    $installedVersion = Get-PythonVersion -PythonExecutable $PackagePython
    if ($installedVersion -ne $PythonVersion) {
        throw "Expected Python $PythonVersion, but restored '$installedVersion'."
    }
}

function Ensure-VirtualEnvironment {
    param(
        [string]$RequirementsPath,
        [string]$RequirementsHash,
        [object]$State
    )

    $statePythonVersion = Get-StateValue -State $State -Name "pythonVersion"
    $stateRequirementsHash = Get-StateValue -State $State -Name "requirementsHash"
    $venvVersion = Get-PythonVersion -PythonExecutable $VenvPython
    $stateMatches = (
        $statePythonVersion -eq $PythonVersion -and
        $stateRequirementsHash -eq $RequirementsHash
    )
    $dependenciesReady = (
        -not $Force -and
        $venvVersion -eq $PythonVersion -and
        $stateMatches -and
        (Test-PythonDependencies -PythonExecutable $VenvPython -Quiet)
    )

    if ($dependenciesReady) {
        Write-Step "Python virtual environment is current"
        return
    }

    if ($ValidateOnly) {
        throw "Python virtual environment is missing, invalid, or out of date."
    }

    Write-Step "Creating a clean Python virtual environment"
    Remove-SafeLocalDirectory -Path $VenvRoot
    Invoke-NativeCommand `
        -FilePath $PackagePython `
        -Arguments @("-m", "venv", $VenvRoot) `
        -Description "Virtual environment creation"

    if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
        throw "Virtual environment did not produce $VenvPython."
    }

    $pipArguments = @(
        "-m", "pip", "install",
        "--disable-pip-version-check"
    )
    if (-not [string]::IsNullOrWhiteSpace($WheelSource)) {
        $resolvedWheelSource = $WheelSource
        if (-not $WheelSource.StartsWith("\\") -and
            -not [System.IO.Path]::IsPathRooted($WheelSource)) {
            $resolvedWheelSource =
                [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot $WheelSource))
        }
        if (-not (Test-Path -LiteralPath $resolvedWheelSource -PathType Container)) {
            throw "Wheel source was not found: $resolvedWheelSource"
        }
        $pipArguments += @(
            "--no-index",
            "--find-links", $resolvedWheelSource
        )
    }
    $pipArguments += @("-r", $RequirementsPath)

    Write-Step "Installing Python dependencies from $(Split-Path -Leaf $RequirementsPath)"
    Invoke-NativeCommand `
        -FilePath $VenvPython `
        -Arguments $pipArguments `
        -Description "Python dependency installation"

    if (-not (Test-PythonDependencies -PythonExecutable $VenvPython)) {
        throw "Python dependency validation failed."
    }
}

function Ensure-Browser {
    if ($SkipChrome) {
        Write-Step "Chrome setup was skipped"
        return
    }

    if (Test-BrowserEnvironment -ExpectedChannel $ChromeChannel) {
        Write-Step "Chrome and ChromeDriver are ready"
        return
    }

    if ($ValidateOnly) {
        throw "Chrome and ChromeDriver are missing or invalid."
    }

    $chromeInstaller = Join-Path $PSScriptRoot "install_chrome_beta.ps1"
    if (-not (Test-Path -LiteralPath $chromeInstaller -PathType Leaf)) {
        throw "Chrome installer was not found: $chromeInstaller"
    }

    Write-Step "Installing Chrome for Testing and ChromeDriver"
    & $chromeInstaller -InstallRoot $ToolsRoot -Channel $ChromeChannel
    if (-not (Test-BrowserEnvironment -ExpectedChannel $ChromeChannel)) {
        throw "Chrome setup completed without a valid browser environment."
    }
}

function Write-EnvironmentFiles {
    param(
        [string]$RequirementsPath,
        [string]$RequirementsHash
    )

    $environmentLines = @(
        "# Auto-generated by ensure_environment.ps1",
        ('$env:VT_WEBGUEST_PYTHON = ''{0}''' -f $VenvPython.Replace("'", "''"))
    )
    if (-not $SkipChrome) {
        $environmentLines += (
            '. ''{0}''' -f $BrowserEnvironmentFile.Replace("'", "''")
        )
    }
    $environmentLines | Set-Content -LiteralPath $EnvironmentFile -Encoding UTF8

    $chromeVersion = ""
    if (Test-Path -LiteralPath $BrowserEnvironmentFile -PathType Leaf) {
        $browserText = Get-Content -LiteralPath $BrowserEnvironmentFile -Raw
        if ($browserText -match "Version:\s*([^\s]+)") {
            $chromeVersion = $Matches[1]
        }
    }

    $state = [ordered]@{
        schemaVersion = 1
        pythonVersion = $PythonVersion
        requirementsFile = [System.IO.Path]::GetFileName($RequirementsPath)
        requirementsHash = $RequirementsHash
        chromePrepared = -not [bool]$SkipChrome
        chromeChannel = $ChromeChannel
        chromeVersion = $chromeVersion
        updatedAtUtc = [DateTime]::UtcNow.ToString("o")
    }
    $state |
        ConvertTo-Json |
        Set-Content -LiteralPath $StatePath -Encoding UTF8
}

New-Item -ItemType Directory -Path $ToolsRoot -Force | Out-Null

$lockStream = $null
$lockDeadline = [DateTime]::UtcNow.AddSeconds($LockTimeoutSec)
while ($null -eq $lockStream) {
    try {
        $lockStream = [System.IO.File]::Open(
            $LockPath,
            [System.IO.FileMode]::OpenOrCreate,
            [System.IO.FileAccess]::ReadWrite,
            [System.IO.FileShare]::None)
    }
    catch [System.IO.IOException] {
        if ([DateTime]::UtcNow -ge $lockDeadline) {
            throw "Timed out waiting for the environment setup lock: $LockPath"
        }
        Start-Sleep -Seconds 1
    }
}

try {
    $requirementsPath = Join-Path $ProjectRoot "requirements.lock"
    if (-not (Test-Path -LiteralPath $requirementsPath -PathType Leaf)) {
        $requirementsPath = Join-Path $ProjectRoot "requirements.txt"
        Write-Warning "requirements.lock is not present; using requirements.txt."
    }
    if (-not (Test-Path -LiteralPath $requirementsPath -PathType Leaf)) {
        throw "No requirements.lock or requirements.txt file was found."
    }

    $requirementsHash = (Get-FileHash -LiteralPath $requirementsPath -Algorithm SHA256).Hash
    $state = Get-State

    Ensure-PackagePython
    Ensure-VirtualEnvironment `
        -RequirementsPath $requirementsPath `
        -RequirementsHash $requirementsHash `
        -State $state
    Ensure-Browser

    if ($ValidateOnly) {
        Write-Step "Environment validation succeeded"
    }
    else {
        Write-EnvironmentFiles `
            -RequirementsPath $requirementsPath `
            -RequirementsHash $requirementsHash
        Write-Step "Environment is ready"
    }

    Write-Host "VT_WEBGUEST_PYTHON=$VenvPython" -ForegroundColor Green
    if (-not $SkipChrome) {
        Write-Host "CHROME_BROWSER_PATH=$env:CHROME_BROWSER_PATH" -ForegroundColor Green
        Write-Host "CHROME_DRIVER_PATH=$env:CHROME_DRIVER_PATH" -ForegroundColor Green
    }
}
finally {
    if ($null -ne $lockStream) {
        $lockStream.Dispose()
    }
}
