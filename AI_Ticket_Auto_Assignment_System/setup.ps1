# AI Ticket Auto Assignment System
# Quick setup script for Windows

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " HelpDesk AI — Setup Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check Python
$pythonVersion = python --version 2>&1
Write-Host "[1/6] Python: $pythonVersion" -ForegroundColor Green

# Create virtual environment
Write-Host "[2/6] Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "[3/6] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Copy .env
Write-Host "[4/6] Setting up .env file..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  Created .env from template. Please update DB credentials!" -ForegroundColor Red
}

# Create directories
Write-Host "[5/6] Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "dataset", "app/ml/saved_models", "app/static/plots", "uploads" | Out-Null

# Database setup
Write-Host "[6/6] Setting up database..." -ForegroundColor Yellow
$env:FLASK_APP = "run.py"
flask init-db

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Train the AI model:"
Write-Host "     flask train-model"
Write-Host ""
Write-Host "  2. Start the application:"
Write-Host "     flask run"
Write-Host ""
Write-Host "  3. Open browser: http://localhost:5000"
Write-Host ""
Write-Host "Login Credentials:" -ForegroundColor Yellow
Write-Host "  Admin    -> admin@company.com / Admin@123456"
Write-Host "  Agent    -> alice@company.com / Password@123"
Write-Host "  Employee -> emma@company.com  / Password@123"
