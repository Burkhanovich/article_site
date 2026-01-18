@echo off
REM Setup script for Windows

echo ========================================
echo Article Publishing Platform Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo [1/7] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/7] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/7] Upgrading pip...
python -m pip install --upgrade pip

echo [4/7] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [5/7] Checking if .env exists...
if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env file with your configuration!
    echo Press any key to continue after editing .env...
    pause
)

echo [6/7] Running database migrations...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Database migration failed
    echo Make sure PostgreSQL is running or switch to SQLite in settings.py
    pause
    exit /b 1
)

echo [7/7] Creating superuser...
echo You will be prompted to create an admin account:
python manage.py createsuperuser

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Generate translations: python manage.py makemessages -l uz -l ru -l en
echo 2. Compile translations: python manage.py compilemessages
echo 3. Collect static files: python manage.py collectstatic
echo 4. Run development server: python manage.py runserver
echo.
echo Then visit: http://127.0.0.1:8000/uz/
echo Admin panel: http://127.0.0.1:8000/uz/admin/
echo.
pause
