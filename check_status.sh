#!/bin/bash

echo "🔍 Checking Smart Habit Tracker Status..."
echo ""

# Check Backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API: Running at http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
else
    echo "❌ Backend API: Not running"
    echo "   Start with: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
fi

# Check Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend: Running at http://localhost:3000"
else
    echo "❌ Frontend: Not running"
    echo "   Start with: cd frontend && npm run dev"
fi

# Check PostgreSQL
if pg_isready -h localhost > /dev/null 2>&1; then
    echo "✅ PostgreSQL: Running"
else
    echo "❌ PostgreSQL: Not running"
fi

# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Running"
else
    echo "⚠️  Redis: Not running (some features may not work)"
    echo "   Start with: brew services start redis"
fi

echo ""
echo "📖 For full setup instructions, see QUICK_START.md"

