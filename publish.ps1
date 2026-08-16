# Auto-generated Publish Script
Write-Host "Cleaning old build files..." -ForegroundColor Cyan
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "*.egg-info") { Remove-Item -Recurse -Force "*.egg-info" }

Write-Host "Building package..." -ForegroundColor Cyan
python -m build

Write-Host "Checking package..." -ForegroundColor Cyan
twine check dist/*

Write-Host "Uploading to PyPI..." -ForegroundColor Yellow
twine upload dist/*

Write-Host "Cleaning up..." -ForegroundColor Green
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "*.egg-info") { Remove-Item -Recurse -Force "*.egg-info" }
