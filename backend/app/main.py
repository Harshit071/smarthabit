from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, habits, habit_logs, goals, analytics, suggestions, gamification
from app.websocket.handlers import websocket_endpoint
from app.database import Base, engine
from app.config import settings
import os

# Create database tables (only in development)
if os.getenv("ENVIRONMENT", "development") == "development":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Habit & Goal Tracker API",
    description="Production-ready real-time habit and goal tracking system",
    version="1.0.0"
)

# CORS middleware - allow all origins in production, specific in dev
allowed_origins = [
    "http://localhost:3000",
    "https://localhost:3000",
]

# Add the deployed frontend URL (both http and https) if available
if settings.FRONTEND_URL:
    allowed_origins.append(settings.FRONTEND_URL)
    if settings.FRONTEND_URL.startswith("http://"):
        allowed_origins.append(settings.FRONTEND_URL.replace("http://", "https://"))
    elif settings.FRONTEND_URL.startswith("https://"):
        allowed_origins.append(settings.FRONTEND_URL.replace("https://", "http://"))


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(habit_logs.router)
app.include_router(goals.router)
app.include_router(analytics.router)
app.include_router(suggestions.router)
app.include_router(gamification.router)

# WebSocket endpoint
app.add_websocket_route("/ws", websocket_endpoint)


@app.get("/")
async def root():
    return {
        "message": "Smart Habit & Goal Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
