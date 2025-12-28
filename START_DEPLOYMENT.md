# 🚀 Start Deployment - Quick Guide

## ⚡ Fastest Path to Live (Railway - 10 minutes)

### Step 1: Push to GitHub (2 min)

```bash
cd /Users/harshit/Desktop/SmartHabbit

# Run deployment helper
./deploy.sh

# OR manually:
git init
git add .
git commit -m "Smart Habit Tracker - Ready for deployment"

# Create repo on GitHub.com (github.com/new)
# Then:
git remote add origin https://github.com/YOUR_USERNAME/smarthabit.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway (8 min)

1. **Go to**: https://railway.app
2. **Login** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select** your repository

### Step 3: Add Services

Railway will auto-detect your backend. Then:

1. **Click "+ New"** → **PostgreSQL**
   - Railway creates it automatically
   - Connection string is auto-set

2. **Click "+ New"** → **Redis**
   - Railway creates it automatically
   - Connection string is auto-set

### Step 4: Configure Backend

1. **Click your backend service**
2. **Settings**:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Variables** tab → Add:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
SECRET_KEY=6NWTCR8XflLZzNUhO0-TQfBWHFcHZymXbDcBcSV-hZs
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
ENVIRONMENT=production
```

4. **Wait for deployment** (2-3 min)
5. **Copy backend URL**: `https://your-app.railway.app`

### Step 5: Deploy Frontend

1. **Add New Service** → **GitHub Repo** (same repo)
2. **Settings**:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview -- --host 0.0.0.0 --port $PORT`

3. **Variables**:
```env
VITE_API_URL=https://your-backend.railway.app
VITE_WS_URL=wss://your-backend.railway.app
```

4. **Update backend CORS**:
   - Backend service → Variables
   - Add: `FRONTEND_URL=https://your-frontend.railway.app`
   - Redeploy backend

### Step 6: Initialize Achievements

After backend deploys, in Railway Shell:

```bash
cd backend
python -c "
from app.database import SessionLocal
from app.services.gamification_service import GamificationService
db = SessionLocal()
GamificationService.initialize_achievements(db)
print('✅ Achievements initialized!')
"
```

### Step 7: Test & Share!

- **Frontend**: `https://your-frontend.railway.app`
- **Backend**: `https://your-backend.railway.app`
- **API Docs**: `https://your-backend.railway.app/docs`

## ✅ You're Live!

Share the frontend URL with users. They can:
- ✅ Register accounts
- ✅ Create habits
- ✅ Earn XP and level up
- ✅ Unlock achievements
- ✅ Track goals in real-time

## 🎯 What Users Will See

- Beautiful gradient UI
- XP and level system
- Achievement badges
- Real-time updates
- Progress tracking
- Gamification features

## 📊 Monitoring

- Railway dashboard shows logs and metrics
- Health check: `/health` endpoint
- API docs always available

---

**Your app is production-ready!** 🎉

