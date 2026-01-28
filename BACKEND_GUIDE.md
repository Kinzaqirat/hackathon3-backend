# LearnFlow Backend - Complete Implementation

Complete FastAPI backend for the LearnFlow learning platform with PostgreSQL, Kafka integration, authentication, and advanced features.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL (or Neon serverless PostgreSQL)
- Kafka cluster (or local Kafka for development)
- OpenAI API key (for chatbot features)

### Installation

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
# or
poetry install
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your actual configuration
```

3. **Initialize database**:
```bash
python -c "from app.core.database import init_db; init_db()"
```

4. **Run the server**:
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📋 API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Register new student
- `POST /login` - Login and get user info
- `POST /change-password` - Change password
- `GET /me` - Get current user profile

### Exercises (`/api/exercises`)
- `GET /` - List all exercises (with filters)
- `GET /{exercise_id}` - Get exercise details
- `POST /` - Create new exercise (admin)
- `PUT /{exercise_id}` - Update exercise (admin)
- `DELETE /{exercise_id}` - Delete exercise (admin)

### Submissions (`/api/submissions`)
- `POST /` - Submit code for exercise
- `GET /{submission_id}` - Get submission details
- `GET /student/{student_id}` - Get student submissions
- `GET /exercise/{exercise_id}` - Get exercise submissions
- `PUT /{submission_id}/evaluate` - Evaluate submission (admin)

### Chat (`/api/chat`)
- `POST /sessions/` - Create chat session
- `GET /sessions/{student_id}` - Get student sessions
- `GET /sessions/{session_id}/messages` - Get session messages
- `POST /sessions/{session_id}/messages` - Send message
- `PUT /sessions/{session_id}/end` - End session
- `WebSocket /ws/{session_id}` - Real-time chat

### Analytics (`/api/analytics`)
- `GET /student/{student_id}/progress` - Student progress
- `GET /student/{student_id}/stats` - Student statistics
- `GET /exercise/{exercise_id}/stats` - Exercise statistics
- `GET /leaderboard` - Top students leaderboard

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Settings & configuration
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── security.py        # Password hashing
│   │   └── __init__.py
│   ├── models/
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── schemas.py         # Pydantic request/response models
│   │   └── __init__.py
│   ├── routes/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── exercises.py       # Exercise management
│   │   ├── submissions.py     # Code submissions
│   │   ├── chat.py            # Chat endpoints
│   │   ├── analytics.py       # Analytics endpoints
│   │   └── __init__.py
│   ├── services/
│   │   ├── auth_service.py    # Auth business logic
│   │   ├── exercise_service.py # Exercise management logic
│   │   ├── chat_service.py    # Chat logic
│   │   ├── kafka_service.py   # Kafka event streaming
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   ├── test_auth.py
│   ├── test_exercises.py
│   ├── test_submissions.py
│   └── conftest.py
├── main.py                    # FastAPI app entry point
├── pyproject.toml            # Poetry configuration
└── .env.example              # Environment template
```

## 🗄️ Database Schema

### Tables
- **students** - User accounts with authentication
- **exercises** - Learning exercises with test cases
- **exercise_submissions** - Student code submissions
- **code_execution_results** - Execution results and logs
- **progress** - Student progress tracking
- **chat_sessions** - Chat session records
- **chat_messages** - Chat message history
- **system_events** - System events and audit logs

## 🔐 Authentication

Session-based authentication with:
- Session IDs stored server-side
- Password hashing with bcrypt
- Session validation on protected routes

```bash
# Get user info
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'

# Use session ID in requests
curl http://localhost:8000/api/auth/me \
  -H "X-Session-ID: YOUR_SESSION_ID"
```

## 📡 Kafka Integration

Event streaming for:
- Student events
- Exercise submissions
- Progress updates
- Chat messages
- System events

Topics:
- `student-events`
- `exercise-submissions`
- `progress-updates`
- `chat-messages`
- `system-events`

## 🤖 Chatbot Features

- Real-time chat with AI agents
- Session-based conversations
- Message history
- WebSocket support for live updates
- OpenAI GPT integration

## 📊 Analytics & Tracking

- Student progress tracking
- Exercise completion statistics
- Leaderboards
- Performance metrics
- Attempt tracking
- Score management

## 🧪 Testing

Run tests with pytest:
```bash
pytest tests/
pytest tests/test_auth.py -v
pytest tests/ --cov=app
```

## 📦 Dependencies

Key packages:
- **fastapi** - Web framework
- **sqlalchemy** - ORM
- **pydantic** - Data validation
- **python-jose** - JWT handling
- **passlib** - Password hashing
- **aiokafka** - Kafka async client
- **openai** - ChatGPT integration
- **psycopg2** - PostgreSQL driver
- **httpx** - Async HTTP client

Full list in `pyproject.toml`

## 🚀 Production Deployment

### Environment Setup
```bash
# Use production database
DATABASE_URL=postgresql://user:pass@neon.tech/learnflow

# Strong JWT secret (generate with: openssl rand -hex 32)
SECRET_KEY=your-production-secret-key

# OpenAI key
OPENAI_API_KEY=sk-your-key

# Kafka cluster
KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9092,kafka3:9092
```

### Run with Gunicorn (production ASGI server)
```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Docker Deployment
See [Dockerfile](../specs/002-hackathon-spec/plan.md) in deployment specifications

## 📝 Example Usage

### Register Student
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "name": "John Doe",
    "password": "securepass123",
    "grade_level": 10
  }'
```

### Create Exercise
```bash
curl -X POST http://localhost:8000/api/exercises \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "description": "Learn Python fundamentals",
    "difficulty_level": "beginner",
    "topic": "python",
    "starter_code": "# Write your code here",
    "expected_output": "Hello World"
  }'
```

### Submit Code
```bash
curl -X POST http://localhost:8000/api/submissions \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "exercise_id": 1,
    "code": "print(\"Hello World\")",
    "language": "python"
  }'
```

## 🔍 Monitoring

- Application health: `GET /health`
- Check database: Verify `DATABASE_URL` connectivity
- Monitor Kafka: Ensure `KAFKA_BOOTSTRAP_SERVERS` accessible
- OpenAI API: Validate `OPENAI_API_KEY`

## 📚 Documentation

- OpenAPI/Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Raw OpenAPI JSON: http://localhost:8000/openapi.json

## 🤝 Contributing

[Development guidelines and contribution process]

## 📄 License

[License information]
