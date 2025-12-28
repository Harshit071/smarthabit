# ⚡ Quick Deploy - Choose Your Platform

## 🥇 Recommended: Railway (Easiest)

**Time**: 10-15 minutes  
**Cost**: Free tier available

### Steps:
1. Push code to GitHub
2. Go to https://railway.app
3. Deploy from GitHub
4. Add PostgreSQL + Redis services
5. Set environment variables
6. Deploy!

**Full Guide**: See `DEPLOY_RAILWAY.md`

---

## 🥈 Best Performance: Vercel + Railway

**Time**: 15-20 minutes  
**Cost**: Free tier for both

### Steps:
1. Deploy backend on Railway (see above)
2. Deploy frontend on Vercel
3. Connect them

**Full Guide**: See `DEPLOY_VERCEL_RAILWAY.md`

---

## 🥉 Alternative: Render

**Time**: 15-20 minutes  
**Cost**: Free tier available

### Steps:
1. Deploy PostgreSQL database
2. Deploy Redis
3. Deploy backend web service
4. Deploy frontend static site

**Full Guide**: See `DEPLOY_RENDER.md`

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure:

- [ ] Code is pushed to GitHub
- [ ] All tests pass (if any)
- [ ] Environment variables documented
- [ ] Database migrations ready
- [ ] CORS settings configured
- [ ] SECRET_KEY generated

---

## 🔑 Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🚀 Quick Start (Railway)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. **Deploy on Railway**:
   - Go to railway.app
   - New Project → GitHub
   - Select repo
   - Add PostgreSQL
   - Add Redis
   - Deploy backend
   - Deploy frontend
   - Set environment variables
   - Done!

3. **Share URL**: Your app is live! 🎉

---

## 💡 Tips

- **Start with Railway** - easiest setup
- **Use managed databases** - less maintenance
- **Set up custom domain** - looks professional
- **Enable auto-deploy** - updates automatically
- **Monitor logs** - catch issues early

---

## 🆘 Troubleshooting

### Backend won't start
- Check environment variables
- Verify database connection
- Check logs in Railway/Render dashboard

### Frontend can't connect
- Verify `VITE_API_URL` is correct
- Check CORS settings in backend
- Ensure backend is running

### Database errors
- Run migrations: `alembic upgrade head`
- Check database URL format
- Verify database is accessible

---

**Ready to deploy? Choose a platform and follow its guide!** 🚀

