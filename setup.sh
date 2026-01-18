#!/bin/bash

# Setup script for Linux/Mac

set -e  # Exit on error

echo "========================================"
echo "Article Publishing Platform Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10+ first"
    exit 1
fi

echo "[1/7] Creating virtual environment..."
python3 -m venv venv

echo "[2/7] Activating virtual environment..."
source venv/bin/activate

echo "[3/7] Upgrading pip..."
pip install --upgrade pip

echo "[4/7] Installing dependencies..."
pip install -r requirements.txt

echo "[5/7] Checking if .env exists..."
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env file with your configuration!"
    echo "Press Enter to continue after editing .env..."
    read
fi

echo "[6/7] Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "[7/7] Creating superuser..."
echo "You will be prompted to create an admin account:"
python manage.py createsuperuser

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Generate translations: python manage.py makemessages -l uz -l ru -l en"
echo "2. Compile translations: python manage.py compilemessages"
echo "3. Collect static files: python manage.py collectstatic"
echo "4. Run development server: python manage.py runserver"
echo ""
echo "Then visit: http://127.0.0.1:8000/uz/"
echo "Admin panel: http://127.0.0.1:8000/uz/admin/"
echo ""
