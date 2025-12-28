# Production Deployment Guide

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)
- ✅ Free tier available
- ✅ Automatic deployments
- ✅ Built-in PostgreSQL & Redis
- ✅ Simple setup

### Option 2: Render
- ✅ Free tier available
- ✅ Easy setup
- ✅ Managed databases

### Option 3: DigitalOcean App Platform
- ✅ Good pricing
- ✅ Managed databases

### Option 4: Vercel (Frontend) + Railway (Backend)
- ✅ Best performance
- ✅ Free tier for both

---

## 🎯 Option 1: Railway Deployment (Recommended)

### Step 1: Prepare for Railway

1. **Create `railway.json`** for configuration
2. **Update environment variables**
3. **Create `Procfile`** for process management

### Step 2: Deploy Backend

1. Go to https://railway.app
2. Sign up/login
3. Click "New Project"
4. Select "Deploy from GitHub repo" (or upload code)
5. Add PostgreSQL service
6. Add Redis service
7. Set environment variables
8. Deploy!

### Step 3: Deploy Frontend

1. Add new service in Railway
2. Select frontend directory
3. Set build command: `npm install && npm run build`
4. Set start command: `npm run preview` (or use Vercel)

### Step 4: Configure Environment Variables

Set these in Railway:
- `POSTGRES_URL` (auto-set by Railway)
- `REDIS_URL` (auto-set by Railway)
- `SECRET_KEY` (generate strong key)
- `FRONTEND_URL` (your frontend URL)
- `BACKEND_URL` (your backend URL)

---

## 🎯 Option 2: Render Deployment

### Backend Deployment

1. Go to https://render.com
2. Create new "Web Service"
3. Connect GitHub repo
4. Settings:
   - Build Command: `cd backend && pip install -r requirements.txt && alembic upgrade head`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database
6. Add Redis instance
7. Set environment variables

### Frontend Deployment

1. Create new "Static Site"
2. Connect GitHub repo
3. Build Command: `cd frontend && npm install && npm run build`
4. Publish Directory: `frontend/dist`
5. Set environment variables

---

## 🎯 Option 3: Vercel + Railway (Best Performance)

### Backend on Railway
- Follow Railway steps above

### Frontend on Vercel
1. Go to https://vercel.com
2. Import GitHub repo
3. Root Directory: `frontend`
4. Build Command: `npm run build`
5. Output Directory: `dist`
6. Set environment variables:
   - `VITE_API_URL`: Your Railway backend URL
   - `VITE_WS_URL`: Your Railway WebSocket URL

---

## 📝 Pre-Deployment Checklist

- [ ] Update CORS settings for production domain
- [ ] Set strong SECRET_KEY
- [ ] Configure production database
- [ ] Set up Redis
- [ ] Update frontend API URLs
- [ ] Test all features
- [ ] Set up SSL/HTTPS
- [ ] Configure domain (optional)

Let me create the deployment files for you!

