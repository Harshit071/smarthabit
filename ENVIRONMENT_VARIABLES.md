# Environment Variables for Production

## 🔑 Required Variables

### Backend (Railway/Render)

```env
# Database (Railway auto-sets these)
DATABASE_URL=${{Postgres.DATABASE_URL}}
# OR manually:
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
POSTGRES_HOST=your_host
POSTGRES_PORT=5432

# Redis (Railway auto-sets)
REDIS_URL=${{Redis.REDIS_URL}}
# OR manually:
REDIS_HOST=your_redis_host
REDIS_PORT=6379
REDIS_DB=0

# JWT Authentication
SECRET_KEY=6NWTCR8XflLZzNUhO0-TQfBWHFcHZymXbDcBcSV-hZs
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}

# Application URLs (set after deployment)
FRONTEND_URL=https://your-frontend.railway.app
BACKEND_URL=https://your-backend.railway.app
ENVIRONMENT=production
```

### Frontend (Vercel/Railway)

```env
VITE_API_URL=https://your-backend.railway.app
VITE_WS_URL=wss://your-backend.railway.app
```

## 🔐 Generate New SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📝 Railway-Specific

Railway uses `${{Service.Variable}}` syntax:
- `${{Postgres.DATABASE_URL}}` - Auto-set by Railway
- `${{Redis.REDIS_URL}}` - Auto-set by Railway

## ✅ Verification

After setting variables, verify:
1. Backend health: `https://your-backend.railway.app/health`
2. Frontend loads: `https://your-frontend.railway.app`
3. API works: Try registering a user

