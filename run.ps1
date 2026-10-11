#Requires -Version 5.1
<#
.SYNOPSIS
    Starts the AccessControl dev stack on Windows: Redis (Docker), Django, Celery worker, Celery beat, Vite.

.DESCRIPTION
    Every service opens in its own PowerShell window, so logs stay separate and a single
    service can be restarted on its own. Press Ctrl+C or close the window to stop a service.

.EXAMPLE
    .\run.ps1 -Setup    # first run: venv, pip/npm dependencies, migrations
    .\run.ps1           # start everything
#>
param(
    # Install dependencies and apply migrations instead of starting the services.
    [switch]$Setup
)

$ErrorActionPreference = 'Stop'

$Backend        = Join-Path $PSScriptRoot 'backend'
$Frontend       = Join-Path $PSScriptRoot 'frontend'
$Python         = Join-Path $Backend 'venv\Scripts\python.exe'
$RedisContainer = 'access-control-redis'

function Fail([string]$Message) {
    Write-Host $Message -ForegroundColor Red
    exit 1
}

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

# Runs a native command and stops the script on a non-zero exit code.
function Invoke-Checked([scriptblock]$Command) {
    & $Command
    if ($LASTEXITCODE -ne 0) { Fail "Command failed: $Command" }
}

function Test-Port([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try { return $client.ConnectAsync('127.0.0.1', $Port).Wait(500) }
    catch { return $false }
    finally { $client.Dispose() }
}

function Install-Dependencies {
    if (-not (Test-Path $Python)) {
        Write-Step 'Creating backend\venv'
        $launcher = if (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { 'python' }
        Invoke-Checked { & $launcher -m venv (Join-Path $Backend 'venv') }
    }

    Write-Step 'Installing backend dependencies'
    Invoke-Checked { & $Python -m pip install -r (Join-Path $Backend 'requirements\base.txt') }

    Write-Step 'Applying migrations'
    Invoke-Checked { & $Python (Join-Path $Backend 'manage.py') migrate }

    Write-Step 'Installing frontend dependencies'
    Invoke-Checked { npm install --prefix $Frontend }
}

# Reuses any Redis already listening on 6379; otherwise starts (or creates) a Docker container.
function Start-Redis {
    if (Test-Port 6379) {
        Write-Step 'Redis is already listening on 6379'
        return
    }
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Fail 'Docker not found. Install Docker Desktop or start Redis on port 6379 yourself.'
    }

    Write-Step "Starting Redis container '$RedisContainer'"
    # Windows PowerShell 5.1 turns redirected stderr of native commands into terminating errors under 'Stop'.
    $ErrorActionPreference = 'Continue'
    docker start $RedisContainer *> $null
    if ($LASTEXITCODE -ne 0) {
        docker run -d --name $RedisContainer -p 127.0.0.1:6379:6379 redis:7 | Out-Null
    }
    if ($LASTEXITCODE -ne 0) { Fail 'Could not start Redis in Docker. Is Docker Desktop running?' }
}

# -NoExit keeps the window open, so a crash traceback stays visible.
function Start-InWindow([string]$Title, [string]$WorkDir, [string]$Command) {
    Write-Step "Starting $Title"
    $full = "`$Host.UI.RawUI.WindowTitle = 'AccessControl - $Title'; $Command"
    Start-Process powershell -WorkingDirectory $WorkDir `
        -ArgumentList "-NoExit -NoProfile -ExecutionPolicy Bypass -Command $full"
}

if (-not (Test-Path (Join-Path $Backend '.env'))) {
    Fail 'backend\.env not found. Copy backend\env.example to backend\.env and fill it in.'
}

if ($Setup) {
    Install-Dependencies
    Write-Host 'Setup complete. Start the project with: .\run.ps1' -ForegroundColor Green
    exit 0
}

if (-not (Test-Path $Python)) { Fail 'backend\venv not found. Run: .\run.ps1 -Setup' }
if (-not (Test-Path (Join-Path $Frontend 'node_modules'))) { Fail 'frontend\node_modules not found. Run: .\run.ps1 -Setup' }
# A second run would start a second beat and every periodic task would fire twice.
if (Test-Port 8000) { Fail 'Port 8000 is busy - the project seems to be running already. Close its windows first.' }

Start-Redis
Start-InWindow 'backend'  $Backend  '.\venv\Scripts\python.exe manage.py runserver'
# The prefork pool is not supported on Windows.
Start-InWindow 'celery'   $Backend  '.\venv\Scripts\python.exe -m celery -A src worker --pool=solo -l INFO'
Start-InWindow 'beat'     $Backend  '.\venv\Scripts\python.exe -m celery -A src beat -l INFO'
Start-InWindow 'frontend' $Frontend 'npm run dev'

Write-Host ''
Write-Host 'Backend:  http://localhost:8000' -ForegroundColor Green
Write-Host 'Frontend: http://localhost:5173' -ForegroundColor Green
Write-Host "Stop: Ctrl+C or close each window. Redis keeps running: docker stop $RedisContainer"
