# LearnFlow Backend API

A production-ready FastAPI backend for the LearnFlow learning platform with advanced features including code execution, progress tracking, chatbot integration, and real-time event streaming.

## ✨ Features

- **🔐 Authentication**: Session-based auth without tokens
- **📚 Exercise Management**: Create, manage, and track exercises
- **💻 Code Submissions**: Submit and evaluate student code
- **📊 Progress Tracking**: Track student progress and analytics
- **🤖 AI Chatbot**: OpenAI-powered chat for student support
- **📡 Event Streaming**: Kafka integration for real-time events
- **🗄️ Database**: PostgreSQL with Neon serverless support
- **🧪 Testing**: Comprehensive test suite with pytest
- **📖 Auto Documentation**: Swagger UI and ReDoc

## 🚀 Quick Start

### 1. Install Dependencies
```bash
poetry install
# or
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

**Required variables:**
- `DATABASE_URL` - PostgreSQL connection string (Neon recommended)
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka cluster addresses
- `OPENAI_API_KEY` - OpenAI API key for chatbot
- `SESSION_SECRET` - Secret for session management

### 3. Initialize Database
```bash
python -c "from app.core.database import init_db; init_db()"
```

### 4. Run Server
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Access:**
- 🌐 API: http://localhost:8000
- 📖 Swagger UI: http://localhost:8000/docs
- 📄 ReDoc: http://localhost:8000/redoc

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new student
- `POST /api/auth/login` - Login (get user info)
- `POST /api/auth/change-password` - Change password
- `GET /api/auth/me` - Current user profile

### Exercises
- `GET /api/exercises/` - List exercises
- `GET /api/exercises/{id}` - Get exercise
- `POST /api/exercises/` - Create exercise
- `PUT /api/exercises/{id}` - Update exercise
- `DELETE /api/exercises/{id}` - Delete exercise

### Submissions
- `POST /api/submissions/` - Submit code
- `GET /api/submissions/{id}` - Get submission
- `GET /api/submissions/student/{student_id}` - Student submissions
- `GET /api/submissions/exercise/{exercise_id}` - Exercise submissions
- `PUT /api/submissions/{id}/evaluate` - Evaluate submission

### Chat
- `POST /api/chat/sessions/` - Create chat session
- `GET /api/chat/sessions/{student_id}` - Get sessions
- `GET /api/chat/sessions/{session_id}/messages` - Get messages
- `POST /api/chat/sessions/{session_id}/messages` - Send message
- `PUT /api/chat/sessions/{session_id}/end` - End session
- `WS /api/chat/ws/{session_id}` - WebSocket connection

### Analytics
- `GET /api/analytics/student/{student_id}/progress` - Student progress
- `GET /api/analytics/student/{student_id}/stats` - Student stats
- `GET /api/analytics/exercise/{exercise_id}/stats` - Exercise stats
- `GET /api/analytics/leaderboard` - Top students

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/              # Core configuration
│   │   ├── config.py      # Settings
│   │   ├── database.py    # SQLAlchemy ORM
│   │   └── security.py    # Password hashing
│   ├── models/            # Database models
│   │   └── models.py      # 8 SQLAlchemy models
│   ├── schemas/           # Request/response models
│   │   └── schemas.py     # 20+ Pydantic schemas
│   ├── routes/            # API endpoints
│   │   ├── auth.py
│   │   ├── exercises.py
│   │   ├── submissions.py
│   │   ├── chat.py
│   │   └── analytics.py
│   ├── services/          # Business logic
│   │   ├── auth_service.py
│   │   ├── exercise_service.py
│   │   ├── chat_service.py
│   │   └── kafka_service.py
│   └── __init__.py
├── tests/                 # Test suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_exercises.py
│   └── test_submissions.py
├── main.py                # FastAPI app
├── pyproject.toml         # Dependencies
├── .env.example           # Config template
└── BACKEND_GUIDE.md       # Detailed guide
```

## 🗄️ Database Schema

**8 Tables:**
- `students` - User accounts
- `exercises` - Learning exercises
- `exercise_submissions` - Code submissions
- `code_execution_results` - Execution logs
- `progress` - Student progress
- `chat_sessions` - Chat history
- `chat_messages` - Messages
- `system_events` - Audit logs

## 🔐 Authentication Flow

```
1. Register/Login → Get user info
2. Use session ID in X-Session-ID header
3. Session expires after 24 hours
```

**Example:**
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}'

# Use token
curl http://localhost:8000/api/auth/me \
  -H "X-Session-ID: SESSION_ID"
```

## 📡 Kafka Topics

Events published to Kafka:
- `student-events` - User actions
- `exercise-submissions` - Code submissions
- `progress-updates` - Progress changes
- `chat-messages` - Chat activity
- `system-events` - System events

## 🤖 Chatbot Integration

OpenAI-powered chatbot with:
- Real-time chat sessions
- Message history
- WebSocket support
- Topic-based conversations
- Multiple agent types

## 📊 Analytics Features

- Completion tracking
- Attempt counting
- Score management
- Leaderboards
- Performance statistics
- Progress visualization

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::test_login_success -v
```

## 📦 Dependencies

**Key packages:**
- `fastapi` - Web framework
- `sqlalchemy` - ORM
- `pydantic` - Data validation
- `bcrypt` - Password hashing
- `passlib` - Password hashing
- `aiokafka` - Kafka client
- `openai` - ChatGPT API
- `psycopg2` - PostgreSQL
- `pytest` - Testing

See `pyproject.toml` for complete list.

## 🚀 Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker (See deployment specs)
Dockerfile available in `specs/002-hackathon-spec/`

### Environment Setup
```
DATABASE_URL=postgresql://user:pass@neon.tech/db
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
OPENAI_API_KEY=sk-your-key
SECRET_KEY=strong-secret-key-123
```

## 📚 Additional Resources

- [Detailed Backend Guide](./BACKEND_GUIDE.md)
- [API Documentation](http://localhost:8000/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)

## 🎯 Next Steps

1. ✅ Backend API complete
2. ⏳ Frontend development (Next.js)
3. ⏳ Deploy to production
4. ⏳ Scale infrastructure
5. ⏳ Add advanced features

## 📝 License

[License information]
