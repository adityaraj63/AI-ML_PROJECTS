#!/usr/bin/env bash
# AI Ticket Auto Assignment System — Linux/Mac setup script

set -e

echo "=================================================="
echo " HelpDesk AI — Setup Script"
echo "=================================================="

# Python check
echo "[1/6] Checking Python..."
python3 --version

# Virtual environment
echo "[2/6] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Dependencies
echo "[3/6] Installing dependencies..."
pip install -r requirements.txt

# .env setup
echo "[4/6] Setting up .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  ⚠️  Created .env from template. Update your DB credentials!"
fi

# Directories
echo "[5/6] Creating directories..."
mkdir -p dataset app/ml/saved_models app/static/plots uploads

# Database
echo "[6/6] Initializing database..."
export FLASK_APP=run.py
flask init-db

echo ""
echo "=================================================="
echo " ✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Train the AI model:"
echo "     flask train-model"
echo ""
echo "  2. Start the application:"
echo "     flask run   (or  python run.py)"
echo ""
echo "  3. Open browser: http://localhost:5000"
echo ""
echo "Login:"
echo "  Admin    → admin@company.com / Admin@123456"
echo "  Agent    → alice@company.com / Password@123"
echo "  Employee → emma@company.com  / Password@123"
