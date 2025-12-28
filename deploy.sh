#!/bin/bash

echo "🚀 Smart Habit Tracker - Deployment Helper"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Smart Habit Tracker with Gamification"
    echo "✅ Git repository initialized"
    echo ""
    echo "📝 Next: Create a repository on GitHub and run:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/smarthabit.git"
    echo "   git push -u origin main"
    echo ""
else
    echo "✅ Git repository exists"
    echo ""
    echo "📤 Pushing to GitHub..."
    git add .
    git commit -m "Update: Ready for deployment" || echo "No changes to commit"
    git push origin main || echo "⚠️  Push failed. Make sure remote is set up."
    echo ""
fi

echo "🎯 Deployment Options:"
echo ""
echo "1. Railway (Easiest):"
echo "   - Go to https://railway.app"
echo "   - New Project → Deploy from GitHub"
echo "   - Add PostgreSQL + Redis"
echo "   - Set environment variables"
echo "   - See DEPLOY_NOW.md for details"
echo ""
echo "2. Vercel + Railway (Best Performance):"
echo "   - Backend on Railway"
echo "   - Frontend on Vercel"
echo "   - See DEPLOY_VERCEL_RAILWAY.md"
echo ""
echo "3. Render:"
echo "   - See DEPLOY_RENDER.md"
echo ""
echo "📚 All deployment guides are in the project root!"
echo ""

