# 🚀 Deploy Now - Step by Step

## Fastest Way: Railway (10 minutes)

### Step 1: Push to GitHub (2 min)

```bash
cd /Users/harshit/Desktop/SmartHabbit

# Initialize git if needed
git init
git add .
git commit -m "Smart Habit Tracker with Gamification"

# Create repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/smarthabit.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway (8 min)

1. **Go to**: https://railway.app
2. **Login** with GitHub
3. **New Project** → "Deploy from GitHub repo"
4. **Select** your `smarthabit` repository
5. **Railway auto-detects** Python project

### Step 3: Add Services

1. **Click "+ New"** → **PostgreSQL**
   - Railway auto-creates database
   - Note the connection string

2. **Click "+ New"** → **Redis**
   - Railway auto-creates Redis
   - Note the connection string

### Step 4: Configure Backend

1. **Click on your backend service**
2. **Settings** → **Root Directory**: `backend`
3. **Settings** → **Start Command**: 
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Variables** tab → Add these:

```env
# Database (Railway auto-sets, but add manually if needed)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis
REDIS_URL=${{Redis.REDIS_URL}}

# JWT Secret (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE

# Other settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
ENVIRONMENT=production
```

5. **Wait for deployment** (2-3 minutes)
6. **Copy your backend URL**: `https://your-app.railway.app`

### Step 5: Configure Frontend

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
   - Go back to backend service
   - Add variable: `FRONTEND_URL=https://your-frontend.railway.app`
   - Redeploy backend

### Step 6: Initialize Achievements

After backend is deployed:

1. **Open Railway Shell** (or use Railway CLI)
2. Run:
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

Or call API:
```bash
curl -X POST https://your-backend.railway.app/api/gamification/init-achievements
```

### Step 7: Test Your Live App!

1. **Frontend URL**: `https://your-frontend.railway.app`
2. **Backend API**: `https://your-backend.railway.app`
3. **API Docs**: `https://your-backend.railway.app/docs`

## ✅ You're Live!

Share the frontend URL with users. They can:
- Register accounts
- Create habits
- Earn XP and level up
- Unlock achievements
- Track goals

## 🎯 Custom Domain (Optional)

1. Go to service settings
2. Click "Generate Domain" or "Add Custom Domain"
3. Update CORS with new domain
4. Update frontend environment variables

## 📊 Monitoring

- **Railway Dashboard**: View logs, metrics, deployments
- **Health Check**: `https://your-backend.railway.app/health`
- **API Docs**: Always available at `/docs`

---

**Your app is now live and ready for users!** 🎉

