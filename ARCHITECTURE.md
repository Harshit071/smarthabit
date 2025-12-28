# Architecture Documentation

## System Architecture

### High-Level Overview

The Smart Habit & Goal Tracker is built as a microservices-ready monolith with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  - React Router for navigation                               │
│  - WebSocket client for real-time updates                   │
│  - Recharts for data visualization                          │
│  - React Query for data fetching                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   REST API   │  │  WebSocket   │  │   Services   │     │
│  │   Endpoints  │  │   Manager    │  │   Layer      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────┬──────────────┬──────────────┬───────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │    Celery    │
│   Database   │  │ Cache/PubSub │  │   Workers    │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Component Details

### 1. Backend Architecture

#### FastAPI Application Structure
```
backend/
├── app/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection & session
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic schemas for validation
│   ├── api/                 # REST API endpoints
│   ├── core/                # Core utilities (auth, redis)
│   ├── services/            # Business logic layer
│   └── websocket/           # WebSocket handlers
└── celery_app/              # Celery task definitions
```

#### Design Patterns Used

1. **Repository Pattern**: Services encapsulate database operations
2. **Dependency Injection**: FastAPI's dependency system for DB sessions, auth
3. **Event-Driven**: Redis pub/sub for decoupled real-time events
4. **Background Jobs**: Celery for async task processing

### 2. Database Schema

#### Core Tables

**users**
- `id` (PK)
- `email` (unique)
- `hashed_password`
- `full_name`
- `is_active`
- `created_at`, `updated_at`

**habits**
- `id` (PK)
- `user_id` (FK)
- `name`, `description`
- `frequency` (daily/weekly/custom)
- `difficulty` (easy/medium/hard)
- `priority` (low/medium/high)
- `status` (active/paused/archived/at_risk)
- `current_streak`, `longest_streak`
- `total_completions`, `total_skips`
- `consistency_score` (0-100)
- `consecutive_misses`
- `last_completed_date`
- `suggested_frequency`
- `failure_rate`
- `created_at`, `updated_at`

**habit_logs**
- `id` (PK)
- `habit_id` (FK)
- `log_date` (date)
- `status` (done/skipped/missed)
- `notes`
- `created_at`, `updated_at`
- Unique constraint: (habit_id, log_date)

**goals**
- `id` (PK)
- `user_id` (FK)
- `name`, `description`
- `target_value`, `current_value`
- `unit`
- `is_completed`, `completed_at`
- `created_at`, `updated_at`

**goal_habits** (junction table)
- `id` (PK)
- `goal_id` (FK)
- `habit_id` (FK)
- `contribution_weight`

### 3. Real-Time Architecture

#### WebSocket Flow

1. **Connection**: Client connects with JWT token in query string
2. **Authentication**: Server validates token and extracts user_id
3. **Subscription**: Server subscribes to Redis channel `user:{user_id}`
4. **Event Broadcasting**: 
   - Services publish events to Redis pub/sub
   - Redis listener forwards to WebSocket manager
   - Manager broadcasts to all user's connections

#### Event Types

- `habit_logged`: When a habit is logged
- `habit_at_risk`: When habit misses 2+ consecutive days
- `goal_completed`: When a goal is achieved
- `nudge`: Smart nudge for inactive habits
- `streak_update`: Real-time streak changes

### 4. Background Jobs (Celery)

#### Scheduled Tasks

1. **Risk Detection** (hourly)
   - Scans all active habits
   - Detects consecutive misses
   - Updates status to "at_risk"
   - Publishes alerts

2. **Daily Nudges** (hourly)
   - Checks for inactive habits (2+ days)
   - Sends WebSocket notifications
   - Sends email reminders (if configured)

3. **Streak Updates** (daily at midnight)
   - Recalculates streaks for all habits
   - Updates consistency scores
   - Refreshes statistics

### 5. Business Logic

#### Consistency Score Formula

```
consistency_score = (completions_in_last_30_days / expected_days) * 100
```

Where `expected_days` depends on frequency:
- Daily: 30 days
- Weekly: ~4 weeks

#### Streak Calculation

1. Get all "done" logs ordered by date (descending)
2. Start from today and count backwards
3. If gap found, streak breaks
4. Update `current_streak` and `longest_streak`

#### Risk Detection Logic

1. Check last 2 days for each active habit
2. If both days missing "done" status → mark as "at_risk"
3. Publish real-time alert
4. Update `consecutive_misses` counter

#### Adaptive Suggestions

- **High Failure Rate (>50%)**: Suggest reducing frequency
- **Low Consistency (<30%)**: Suggest easier difficulty
- **Broken Streak**: Encourage restart with smaller goals

### 6. API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

#### Habits
- `POST /api/habits` - Create habit
- `GET /api/habits` - List all habits
- `GET /api/habits/{id}` - Get habit details
- `PUT /api/habits/{id}` - Update habit
- `DELETE /api/habits/{id}` - Delete habit

#### Habit Logs
- `POST /api/habit-logs` - Log habit (done/skipped)
- `GET /api/habit-logs/habit/{id}` - Get logs for habit

#### Goals
- `POST /api/goals` - Create goal
- `GET /api/goals` - List all goals
- `GET /api/goals/{id}` - Get goal details
- `PUT /api/goals/{id}` - Update goal
- `DELETE /api/goals/{id}` - Delete goal

#### Analytics
- `GET /api/analytics/dashboard` - Dashboard stats
- `GET /api/analytics/habits/{id}/heatmap` - Heatmap data
- `GET /api/analytics/habits/{id}/weekly` - Weekly stats
- `GET /api/analytics/habits/{id}/monthly` - Monthly stats
- `GET /api/analytics/habits/{id}/consistency-trend` - Trend data

#### Suggestions
- `GET /api/suggestions/habits/{id}/adaptive` - Get suggestions
- `POST /api/suggestions/detect-risks` - Manual risk detection

#### WebSocket
- `WS /ws?token={jwt_token}` - Real-time connection

### 7. Security

#### JWT Authentication
- Token-based authentication
- Tokens expire after 30 minutes (configurable)
- Stored in localStorage (frontend)
- Sent in Authorization header (REST) or query param (WebSocket)

#### Password Security
- Bcrypt hashing with salt rounds
- Passwords never stored in plain text

#### CORS
- Configured for frontend origin
- Credentials enabled for cookies (if needed)

### 8. Caching Strategy

#### Redis Cache Usage
- User sessions (optional)
- Frequently accessed analytics
- Dashboard statistics (TTL: 1 hour)

#### Cache Invalidation
- On habit log → invalidate habit stats
- On goal update → invalidate goal progress
- On streak update → invalidate dashboard

### 9. Scalability Considerations

#### Horizontal Scaling
- **Stateless API**: FastAPI instances can scale horizontally
- **Redis Pub/Sub**: Enables cross-instance communication
- **Database Connection Pooling**: SQLAlchemy pool size: 10, overflow: 20
- **WebSocket**: Connection manager per instance (can use Redis for shared state)

#### Performance Optimizations
- Database indexes on frequently queried fields
- Connection pooling
- Async/await for I/O operations
- Background job processing for heavy operations

### 10. Deployment Architecture

#### Docker Compose Setup
- **PostgreSQL**: Persistent data storage
- **Redis**: Cache and message broker
- **Backend**: FastAPI application
- **Celery Worker**: Background task processor
- **Celery Beat**: Scheduled task scheduler
- **Frontend**: React development server

#### Production Considerations
- Use production WSGI server (Gunicorn + Uvicorn workers)
- Nginx reverse proxy
- SSL/TLS certificates
- Environment-based configuration
- Database migrations (Alembic)
- Logging and monitoring
- Health checks

## Design Decisions Explained

### Why FastAPI?
- **Async Support**: Native async/await for high concurrency
- **Type Safety**: Pydantic models provide runtime validation
- **Auto Documentation**: OpenAPI/Swagger docs generated automatically
- **WebSocket Support**: Built-in WebSocket support
- **Performance**: One of the fastest Python frameworks

### Why Redis Pub/Sub?
- **Decoupling**: Services don't need direct WebSocket references
- **Scalability**: Multiple FastAPI instances can share events
- **Reliability**: Redis handles message delivery
- **Flexibility**: Easy to add new event types

### Why Celery?
- **Async Processing**: Long-running tasks don't block API
- **Scheduling**: Built-in support for periodic tasks
- **Retry Logic**: Automatic retries for failed tasks
- **Monitoring**: Flower for task monitoring
- **Scalability**: Multiple workers can process tasks in parallel

### Why WebSockets?
- **Real-Time**: Instant updates without polling
- **Efficiency**: Lower overhead than HTTP polling
- **Bidirectional**: Server can push updates anytime
- **User Experience**: Immediate feedback on actions

### Why React Query?
- **Caching**: Automatic caching of API responses
- **Background Updates**: Refetch on window focus
- **Optimistic Updates**: Update UI before server confirms
- **Error Handling**: Built-in error states

### Database Design Decisions

1. **Separate Logs Table**: 
   - Allows historical analysis
   - Easy to query by date ranges
   - Unique constraint prevents duplicates

2. **Junction Table for Goals**:
   - Many-to-many relationship
   - Contribution weights for flexible goal tracking

3. **Denormalized Stats**:
   - Streak, consistency stored on habit
   - Faster reads, slower writes (acceptable trade-off)

4. **Status Enum**:
   - Clear state management
   - Easy filtering and queries

## Future Enhancements

1. **Mobile App**: React Native with same backend
2. **Social Features**: Share habits, challenges
3. **AI Suggestions**: ML-based habit recommendations
4. **Gamification**: Points, badges, leaderboards
5. **Export Data**: CSV/PDF reports
6. **Reminders**: Push notifications, SMS
7. **Habit Templates**: Pre-defined habit suggestions
8. **Team Goals**: Collaborative goal tracking

