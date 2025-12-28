# 🎨 Render Deployment Guide

## Step 1: Deploy PostgreSQL Database

1. Go to https://render.com
2. **New** → **PostgreSQL**
3. Name: `smarthabit-db`
4. Plan: Free (or paid)
5. **Create Database**
6. Copy **Internal Database URL**

## Step 2: Deploy Redis

1. **New** → **Redis**
2. Name: `smarthabit-redis`
3. Plan: Free (or paid)
4. **Create Redis**
5. Copy **Internal Redis URL**

## Step 3: Deploy Backend

1. **New** → **Web Service**
2. Connect GitHub repository
3. **Settings**:
   - **Name**: `smarthabit-backend`
   - **Environment**: Python 3
   - **Root Directory**: `backend`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && alembic upgrade head
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free (or paid)

4. **Environment Variables**:
   ```
   DATABASE_URL=<from PostgreSQL service>
   REDIS_URL=<from Redis service>
   SECRET_KEY=<generate strong key>
   FRONTEND_URL=https://your-frontend.onrender.com
   BACKEND_URL=https://your-backend.onrender.com
   ENVIRONMENT=production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   CELERY_BROKER_URL=<same as REDIS_URL>
   CELERY_RESULT_BACKEND=<same as REDIS_URL>
   ```

5. **Create Web Service**

## Step 4: Deploy Frontend

1. **New** → **Static Site**
2. Connect GitHub repository
3. **Settings**:
   - **Name**: `smarthabit-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. **Environment Variables**:
   ```
   VITE_API_URL=https://your-backend.onrender.com
   VITE_WS_URL=wss://your-backend.onrender.com
   ```

5. **Create Static Site**

## Step 5: Initialize Achievements

After backend deploys, SSH into service or use Render Shell:
```bash
python -c "
from app.database import SessionLocal
from app.services.gamification_service import GamificationService
db = SessionLocal()
GamificationService.initialize_achievements(db)
print('✅ Achievements initialized!')
"
```

## ✅ Done!

Your app is live on Render!

