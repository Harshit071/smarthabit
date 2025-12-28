# 🚀 Deploy: Vercel (Frontend) + Railway (Backend)

## Best Performance Setup

### Part 1: Deploy Backend on Railway

Follow `DEPLOY_RAILWAY.md` steps 1-3 to deploy backend.

**Get your Railway backend URL**: `https://your-app.railway.app`

### Part 2: Deploy Frontend on Vercel

1. **Go to Vercel**: https://vercel.com
2. **Sign up/Login** (use GitHub)
3. **New Project** → Import GitHub repository
4. **Configure Project**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

5. **Environment Variables**:
   ```
   VITE_API_URL=https://your-backend.railway.app
   VITE_WS_URL=wss://your-backend.railway.app
   ```

6. **Deploy!**

### Part 3: Update CORS

In Railway backend environment variables:
```
FRONTEND_URL=https://your-app.vercel.app
```

Redeploy backend.

## ✅ Done!

- **Frontend**: `https://your-app.vercel.app` (fast CDN)
- **Backend**: `https://your-backend.railway.app`

Share the Vercel URL with users!

