# Smart Habit & Goal Tracker

A production-ready real-time habit and goal tracking system with advanced analytics, risk detection, and adaptive suggestions.

## Architecture Overview

### High-Level Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │◄────►│   FastAPI    │◄────►│ PostgreSQL  │
│  Frontend   │ WS   │   Backend    │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├────► Redis (Cache + Pub/Sub)
                            │
                            └────► Celery Workers
```

### Key Components

1. **FastAPI Backend**: Async REST API + WebSocket server
2. **PostgreSQL**: Primary data store with SQLAlchemy ORM
3. **Redis**: 
   - Caching layer for frequently accessed data
   - Pub/Sub for real-time event broadcasting
   - Celery broker for task queue
4. **Celery**: Background task processing (nudges, analytics, risk detection)
5. **React Frontend**: Real-time UI with WebSocket integration
6. **WebSockets**: Real-time bidirectional communication

### Design Decisions

#### Why FastAPI?
- Native async/await support for high concurrency
- Automatic OpenAPI documentation
- Type hints and validation with Pydantic
- Excellent WebSocket support

#### Why Redis Pub/Sub?
- Decouples event producers from WebSocket connections
- Scales horizontally - multiple FastAPI instances can share events
- Low latency for real-time notifications
- Enables cross-instance communication in distributed deployments

#### Why Celery?
- Long-running tasks (analytics, risk detection) don't block API
- Scheduled tasks (daily nudges, streak calculations)
- Retry logic for failed operations
- Horizontal scaling of background workers

#### Why WebSockets?
- Real-time bidirectional communication
- Lower latency than polling
- Efficient for frequent updates (streaks, risk alerts)

## Project Structure

```
SmartHabbit/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── core/
│   │   ├── services/
│   │   └── websocket/
│   ├── celery_app/
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

1. **Clone and setup environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Start with Docker:**
```bash
docker-compose up -d
```

3. **Run migrations:**
```bash
docker-compose exec backend alembic upgrade head
```

4. **Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Features

- ✅ JWT Authentication
- ✅ Habit Management (CRUD)
- ✅ Daily Habit Logging
- ✅ Real-time Streak Updates
- ✅ Goal Management
- ✅ Analytics Dashboard
- ✅ Habit Risk Detection
- ✅ Adaptive Suggestions
- ✅ Smart Nudging Engine
- ✅ Multi-user Real-time Support

