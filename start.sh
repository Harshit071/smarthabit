#!/bin/bash

# Smart Habit Tracker - Startup Script

echo "🚀 Starting Smart Habit Tracker..."

# Check if PostgreSQL is running
if ! pg_isready -h localhost > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Please start it first:"
    echo "   brew services start postgresql@15"
    echo "   OR: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15"
    exit 1
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running. Starting Redis..."
    echo "   Install: brew install redis"
    echo "   Start: brew services start redis"
    echo "   OR: docker run -d -p 6379:6379 redis:7-alpine"
    echo ""
    echo "Continuing without Redis (some features may not work)..."
fi

# Setup backend
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating backend .env file..."
    cat > .env << 'ENVEOF'
POSTGRES_USER=smarthabit
POSTGRES_PASSWORD=smarthabit_password
POSTGRES_DB=smarthabit_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
ENVEOF
fi

# Run migrations
echo "🗄️  Running database migrations..."
alembic upgrade head 2>&1 | grep -v "INFO" || echo "Migrations completed"

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install --silent
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    cat > .env << 'ENVEOF'
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
ENVEOF
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application, open 3 terminal windows and run:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "Terminal 2 (Celery Worker):"
echo "  cd backend && source venv/bin/activate && celery -A celery_app.celery_app worker --loglevel=info"
echo ""
echo "Terminal 3 (Frontend):"
echo "  cd frontend && npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""

