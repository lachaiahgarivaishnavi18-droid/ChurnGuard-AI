$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Create the Python 3.12 virtual environment and install backend/requirements.txt first. See README.md.'
}
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'frontend\dist\index.html'))) {
    throw 'Build the frontend with npm run build in frontend first. See README.md.'
}
Push-Location (Join-Path $projectRoot 'backend')
try {
    & $pythonPath -m flask --app run db upgrade
    if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
    Write-Host 'Open http://127.0.0.1:5088 (or the port configured in backend/.env). Press Ctrl+C to stop.'
    & $pythonPath run.py
} finally {
    Pop-Location
}
