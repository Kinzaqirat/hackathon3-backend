#!/usr/bin/env bash

# LearnFlow Backend Startup Script
# Comprehensive setup and validation before running

set -e

echo "🚀 LearnFlow Backend Startup Script"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found. Please install Python 3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"

# Check if venv exists, create if not
echo ""
echo "📦 Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || {
    echo -e "${RED}❌ Could not activate virtual environment${NC}"
    exit 1
}
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install/upgrade dependencies
echo ""
echo "📥 Installing dependencies..."
if [ -f "pyproject.toml" ]; then
    pip install -q poetry
    poetry install
else
    pip install -q -r requirements.txt 2>/dev/null || {
        echo -e "${YELLOW}⚠ No requirements.txt found, installing key packages...${NC}"
        pip install -q fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-jose passlib aiokafka openai python-dotenv
    }
fi
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check .env file
echo ""
echo "⚙️ Checking configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Copying .env.example to .env..."
        cp .env.example .env
        echo -e "${YELLOW}⚠ Please edit .env with your configuration:${NC}"
        echo "   - DATABASE_URL: PostgreSQL connection string"
        echo "   - KAFKA_BOOTSTRAP_SERVERS: Kafka addresses"
        echo "   - SECRET_KEY: JWT secret (generate with: openssl rand -hex 32)"
        echo "   - OPENAI_API_KEY: OpenAI API key"
    else
        echo -e "${RED}❌ No .env or .env.example file found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env file found${NC}"
fi

# Validate imports
echo ""
echo "🔍 Validating Python imports..."
python -c "
import sys
try:
    import fastapi
    import sqlalchemy
    import pydantic
    import aiokafka
    import openai
    import jose
    print('✓ All critical imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || exit 1

# Initialize database
echo ""
echo "🗄️ Initializing database..."
python -c "
from app.core.database import init_db
try:
    init_db()
    print('✓ Database initialized')
except Exception as e:
    print(f'⚠ Warning: {e}')
    print('  (Database may already exist or connection failed)')
" || true

# Summary
echo ""
echo "===================================="
echo -e "${GREEN}✅ Backend ready to start!${NC}"
echo ""
echo "🚀 Start the server with:"
echo "   python -m uvicorn main:app --reload"
echo ""
echo "📖 API Documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "💡 Quick test:"
echo "   curl http://localhost:8000/health"
echo ""
