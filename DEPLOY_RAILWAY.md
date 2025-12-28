# 🚂 Railway Deployment Guide (Easiest)

## Step-by-Step Deployment

### Prerequisites
- GitHub account
- Railway account (free at https://railway.app)

### Step 1: Push to GitHub

```bash
# Initialize git if not already
git init
git add .
git commit -m "Initial commit with gamification"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/smarthabit.git
git push -u origin main
```

### Step 2: Deploy Backend on Railway

1. **Go to Railway**: https://railway.app
2. **Sign up/Login** (use GitHub)
3. **New Project** → "Deploy from GitHub repo"
4. **Select your repository**
5. **Add Service** → "PostgreSQL" (Railway auto-creates)
6. **Add Service** → "Redis" (Railway auto-creates)
7. **Configure Backend Service**:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt && alembic upgrade head`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Set Environment Variables

In Railway dashboard, go to your backend service → Variables:

```env
# Database (Railway auto-sets these, but verify)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (Railway auto-sets)
REDIS_URL=${{Redis.REDIS_URL}}

# JWT
SECRET_KEY=your-very-secure-secret-key-here-generate-with-openssl
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}

# Application URLs (set after getting Railway URLs)
FRONTEND_URL=https://your-frontend.railway.app
BACKEND_URL=https://your-backend.railway.app
ENVIRONMENT=production
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 4: Deploy Frontend on Railway

1. **Add New Service** → "GitHub Repo" (same repo)
2. **Root Directory**: `frontend`
3. **Build Command**: `npm install && npm run build`
4. **Start Command**: `npm run preview -- --host 0.0.0.0 --port $PORT`
5. **Set Environment Variables**:
   ```env
   VITE_API_URL=https://your-backend.railway.app
   VITE_WS_URL=wss://your-backend.railway.app
   ```

### Step 5: Initialize Achievements

After backend deploys, run:
```bash
# Via Railway CLI or API
railway run python -c "
from app.database import SessionLocal
from app.services.gamification_service import GamificationService
db = SessionLocal()
GamificationService.initialize_achievements(db)
print('✅ Achievements initialized!')
"
```

Or call the API endpoint:
```bash
curl -X POST https://your-backend.railway.app/api/gamification/init-achievements \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 6: Get Your URLs

1. Railway provides URLs automatically
2. Update `FRONTEND_URL` and `BACKEND_URL` in backend variables
3. Update `VITE_API_URL` and `VITE_WS_URL` in frontend variables
4. Redeploy both services

### Step 7: Custom Domain (Optional)

1. Go to service settings
2. Click "Generate Domain" or "Add Custom Domain"
3. Update CORS settings with new domain

## ✅ Verification

1. **Backend Health**: `https://your-backend.railway.app/health`
2. **API Docs**: `https://your-backend.railway.app/docs`
3. **Frontend**: `https://your-frontend.railway.app`

## 🎉 Done!

Your app is now live! Share the frontend URL with users.

