@echo off
REM LearnFlow Backend Startup Script for Windows
REM Comprehensive setup and validation before running

echo.
echo 🚀 LearnFlow Backend Startup Script
echo ====================================
echo.

REM Check Python
echo 📋 Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+
    exit /b 1
)
python --version
echo ✓ Python found
echo.

REM Check/create venv
echo 📦 Checking virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Install dependencies
echo 📥 Installing dependencies...
if exist "pyproject.toml" (
    pip install -q poetry
    poetry install
) else (
    pip install -q fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-jose passlib aiokafka openai python-dotenv
)
echo ✓ Dependencies installed
echo.

REM Check .env
echo ⚙️ Checking configuration...
if not exist ".env" (
    if exist ".env.example" (
        echo Copying .env.example to .env...
        copy .env.example .env
        echo ⚠ Please edit .env with your configuration:
        echo    - DATABASE_URL: PostgreSQL connection string
        echo    - KAFKA_BOOTSTRAP_SERVERS: Kafka addresses
        echo    - SECRET_KEY: JWT secret
        echo    - OPENAI_API_KEY: OpenAI API key
    ) else (
        echo ❌ No .env or .env.example file found
        exit /b 1
    )
) else (
    echo ✓ .env file found
)
echo.

REM Validate imports
echo 🔍 Validating Python imports...
python -c "import fastapi; import sqlalchemy; import pydantic; print('✓ All imports OK')" || exit /b 1
echo.

REM Summary
echo ====================================
echo ✅ Backend ready to start!
echo.
echo 🚀 Start the server with:
echo    python -m uvicorn main:app --reload
echo.
echo 📖 API Documentation:
echo    http://localhost:8000/docs
echo.
echo 💡 Quick test:
echo    curl http://localhost:8000/health
echo.
