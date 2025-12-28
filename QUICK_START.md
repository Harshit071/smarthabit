# Quick Start Guide

## Option 1: Using Docker (Recommended)

If you have Docker installed:

```bash
# 1. Start all services
docker compose up -d --build

# 2. Run database migrations
docker compose exec backend alembic upgrade head

# 3. Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Option 2: Local Development (Without Docker)

### Prerequisites Setup

1. **Create PostgreSQL database:**
```bash
psql postgres
CREATE USER smarthabit WITH PASSWORD 'smarthabit_password';
CREATE DATABASE smarthabit_db OWNER smarthabit;
\q
```

2. **Start Redis (if not running):**
```bash
brew install redis
brew services start redis
```

### Start the Application

Open **3 terminal windows**:

**Terminal 1 - Backend API:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Celery Worker (Background Jobs):**
```bash
cd backend
source venv/bin/activate
celery -A celery_app.celery_app worker --loglevel=info
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### First Steps

1. Open http://localhost:3000
2. Click "Register" to create an account
3. Create your first habit
4. Log it as "done"
5. Check the dashboard for stats!

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Create database if needed
psql postgres -c "CREATE DATABASE smarthabit_db;"
```

### Redis Connection Error
```bash
# Install and start Redis
brew install redis
brew services start redis

# Or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Port Already in Use
Change ports in `.env` files or kill the process:
```bash
lsof -ti:8000 | xargs kill  # Backend
lsof -ti:3000 | xargs kill  # Frontend
```

