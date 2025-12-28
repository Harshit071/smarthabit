# Running the App Locally (Without Docker)

## Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** and npm installed
3. **PostgreSQL** running locally
4. **Redis** running locally

## Step 1: Install PostgreSQL

### macOS (using Homebrew)
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Create Database
```bash
createdb smarthabit_db
# Or using psql:
psql postgres
CREATE DATABASE smarthabit_db;
CREATE USER smarthabit WITH PASSWORD 'smarthabit_password';
GRANT ALL PRIVILEGES ON DATABASE smarthabit_db TO smarthabit;
\q
```

## Step 2: Install Redis

### macOS
```bash
brew install redis
brew services start redis
```

### Linux
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### Verify Redis
```bash
redis-cli ping
# Should return: PONG
```

## Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
POSTGRES_USER=smarthabit
POSTGRES_PASSWORD=smarthabit_password
POSTGRES_DB=smarthabit_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
EOF

# Run database migrations
alembic upgrade head

# If migrations don't exist, create them:
# alembic revision --autogenerate -m "Initial migration"
# alembic upgrade head
```

## Step 4: Start Backend Services

### Terminal 1: FastAPI Server
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Celery Worker
```bash
cd backend
source venv/bin/activate
celery -A celery_app.celery_app worker --loglevel=info
```

### Terminal 3: Celery Beat (Scheduler)
```bash
cd backend
source venv/bin/activate
celery -A celery_app.celery_app beat --loglevel=info
```

## Step 5: Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
EOF

# Start development server
npm run dev
```

## Step 6: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Quick Test

1. Open http://localhost:3000
2. Register a new account
3. Create a habit
4. Log the habit as "done"
5. Check the dashboard for stats

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running: `pg_isready`
- Check credentials in `.env`
- Verify database exists: `psql -l | grep smarthabit`

### Redis Connection Error
- Ensure Redis is running: `redis-cli ping`
- Check Redis is listening: `redis-cli info server`

### Port Already in Use
- Change ports in `.env` and restart services
- Kill process using port: `lsof -ti:8000 | xargs kill`

### Migration Errors
```bash
# Reset database (WARNING: deletes all data)
dropdb smarthabit_db
createdb smarthabit_db
alembic upgrade head
```

## Alternative: Install Docker

If you prefer Docker:

1. **Install Docker Desktop**: https://www.docker.com/products/docker-desktop
2. Then run:
   ```bash
   docker compose up -d --build
   docker compose exec backend alembic upgrade head
   ```

