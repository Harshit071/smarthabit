# Smart Habit & Goal Tracker - Project Summary

## Overview

A production-ready, real-time habit and goal tracking system built with FastAPI, React, PostgreSQL, Redis, and Celery. The system provides comprehensive habit management, goal tracking, real-time analytics, and intelligent risk detection.

## Key Features Implemented

### ✅ Core Features

1. **User Authentication**
   - JWT-based authentication
   - Secure password hashing with bcrypt
   - User registration and login
   - Protected API endpoints

2. **Habit Management**
   - Create, read, update, delete habits
   - Habit properties: frequency, difficulty, priority
   - Status tracking: active, paused, archived, at_risk
   - Daily habit logging (done/skipped/missed)

3. **Real-Time Updates**
   - WebSocket integration for live updates
   - Redis pub/sub for event broadcasting
   - Real-time streak updates
   - Instant notifications

4. **Goal Management**
   - Create goals with target values
   - Multiple habits can contribute to a goal
   - Automatic progress tracking
   - Goal completion detection

5. **Analytics Dashboard**
   - Live habit heatmap (GitHub-style)
   - Weekly and monthly statistics
   - Consistency trend graphs
   - Overall dashboard statistics

6. **Habit Risk Detection**
   - Automatic detection of habits at risk
   - 2+ consecutive misses → "at_risk" status
   - Real-time alerts via WebSocket
   - Background job monitoring

7. **Adaptive Suggestions**
   - Failure rate analysis
   - Frequency reduction suggestions
   - Difficulty adjustment recommendations
   - Streak recovery encouragement

8. **Smart Nudging Engine**
   - Inactivity detection (2+ days)
   - WebSocket notifications
   - Email reminders (configurable)
   - Background job scheduling

9. **Multi-User Support**
   - User isolation
   - Per-user WebSocket channels
   - Redis pub/sub per user
   - Scalable architecture

## Technology Stack

### Backend
- **FastAPI**: Async Python web framework
- **PostgreSQL**: Primary database
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **Redis**: Caching and pub/sub messaging
- **Celery**: Background task processing
- **JWT**: Authentication tokens
- **WebSockets**: Real-time communication

### Frontend
- **React**: UI framework
- **React Router**: Navigation
- **React Query**: Data fetching and caching
- **Recharts**: Data visualization
- **WebSocket API**: Real-time updates
- **Vite**: Build tool

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Project Structure

```
SmartHabbit/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py             # Configuration
│   │   ├── database.py          # DB connection
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── api/                 # REST endpoints
│   │   ├── core/                # Core utilities
│   │   ├── services/            # Business logic
│   │   └── websocket/           # WebSocket handlers
│   ├── celery_app/              # Celery tasks
│   ├── alembic/                 # Database migrations
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── contexts/            # React contexts
│   │   ├── services/            # API services
│   │   └── App.jsx              # Main app
│   └── package.json             # Node dependencies
├── docker-compose.yml            # Docker orchestration
├── README.md                     # Main README
├── ARCHITECTURE.md              # Architecture docs
├── DEPLOYMENT.md                # Deployment guide
└── API_DOCUMENTATION.md         # API reference
```

## Business Logic Highlights

### Consistency Score Formula
```
consistency_score = (completions_in_last_30_days / expected_days) * 100
```

### Streak Calculation
- Counts consecutive days with "done" status
- Starts from today and works backwards
- Breaks on first gap

### Risk Detection
- Checks last 2 days for each active habit
- If both days missing "done" → mark as "at_risk"
- Publishes real-time alert

### Adaptive Suggestions
- High failure rate (>50%) → suggest reduce frequency
- Low consistency (<30%) → suggest easier difficulty
- Broken streak → encourage restart

## API Endpoints Summary

### Authentication
- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Current user

### Habits
- `POST /api/habits` - Create
- `GET /api/habits` - List
- `GET /api/habits/{id}` - Get
- `PUT /api/habits/{id}` - Update
- `DELETE /api/habits/{id}` - Delete

### Habit Logs
- `POST /api/habit-logs` - Log habit
- `GET /api/habit-logs/habit/{id}` - Get logs

### Goals
- `POST /api/goals` - Create
- `GET /api/goals` - List
- `GET /api/goals/{id}` - Get
- `PUT /api/goals/{id}` - Update
- `DELETE /api/goals/{id}` - Delete

### Analytics
- `GET /api/analytics/dashboard` - Dashboard stats
- `GET /api/analytics/habits/{id}/heatmap` - Heatmap
- `GET /api/analytics/habits/{id}/weekly` - Weekly stats
- `GET /api/analytics/habits/{id}/monthly` - Monthly stats
- `GET /api/analytics/habits/{id}/consistency-trend` - Trend

### Suggestions
- `GET /api/suggestions/habits/{id}/adaptive` - Suggestions
- `POST /api/suggestions/detect-risks` - Risk detection

### WebSocket
- `WS /ws?token={jwt}` - Real-time connection

## Real-Time Events

1. **habit_logged**: When habit is logged
2. **habit_at_risk**: When habit misses 2+ days
3. **goal_completed**: When goal is achieved
4. **nudge**: Smart nudge for inactive habits
5. **streak_update**: Real-time streak changes

## Background Jobs (Celery)

1. **Risk Detection** (hourly)
   - Scans all active habits
   - Detects consecutive misses
   - Updates status

2. **Daily Nudges** (hourly)
   - Checks inactive habits
   - Sends notifications

3. **Streak Updates** (daily)
   - Recalculates streaks
   - Updates consistency scores

## Quick Start

1. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Run Migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. **Access Application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## Design Decisions

### Why FastAPI?
- Native async/await support
- Automatic OpenAPI documentation
- Type safety with Pydantic
- Excellent WebSocket support

### Why Redis Pub/Sub?
- Decouples event producers from WebSocket
- Enables horizontal scaling
- Low latency for real-time events

### Why Celery?
- Long-running tasks don't block API
- Scheduled tasks support
- Retry logic for failures
- Horizontal scaling

### Why WebSockets?
- Real-time bidirectional communication
- Lower latency than polling
- Efficient for frequent updates

## Database Schema

### Core Tables
- **users**: User accounts
- **habits**: Habit definitions
- **habit_logs**: Daily habit logs
- **goals**: Goal definitions
- **goal_habits**: Goal-habit relationships

### Key Relationships
- User → Habits (1:N)
- User → Goals (1:N)
- Habit → Logs (1:N)
- Goal → Habits (N:M via goal_habits)

## Security Features

- JWT token authentication
- Bcrypt password hashing
- CORS configuration
- SQL injection protection (SQLAlchemy)
- Input validation (Pydantic)

## Scalability

- Stateless API (horizontal scaling)
- Connection pooling
- Redis for caching
- Background job processing
- Database indexes on key fields

## Future Enhancements

1. Mobile app (React Native)
2. Social features (sharing, challenges)
3. AI-powered suggestions
4. Gamification (points, badges)
5. Data export (CSV/PDF)
6. Push notifications
7. Habit templates
8. Team goals

## Documentation

- **README.md**: Overview and quick start
- **ARCHITECTURE.md**: Detailed architecture explanation
- **DEPLOYMENT.md**: Production deployment guide
- **API_DOCUMENTATION.md**: Complete API reference

## Testing

Currently not implemented. Recommended:
- Unit tests for services
- Integration tests for API
- E2E tests for frontend
- Load testing for WebSocket

## Monitoring

Recommended tools:
- **Flower**: Celery monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions:
1. Check documentation files
2. Review logs: `docker-compose logs`
3. Check API docs: `/docs` endpoint

---

**Built with ❤️ using FastAPI, React, and modern best practices**

