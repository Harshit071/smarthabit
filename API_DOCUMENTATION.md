# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

### Register User

**POST** `/api/auth/register`

Request body:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

Response: `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

### Login

**POST** `/api/auth/login`

Request (form data):
```
username: user@example.com
password: securepassword
```

Response: `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Get Current User

**GET** `/api/auth/me`

Response: `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

## Habits

### Create Habit

**POST** `/api/habits`

Request body:
```json
{
  "name": "Morning Exercise",
  "description": "30 minutes of exercise every morning",
  "frequency": "daily",
  "difficulty": "medium",
  "priority": "high"
}
```

Response: `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Morning Exercise",
  "description": "30 minutes of exercise every morning",
  "frequency": "daily",
  "difficulty": "medium",
  "priority": "high",
  "status": "active",
  "current_streak": 0,
  "longest_streak": 0,
  "total_completions": 0,
  "total_skips": 0,
  "consistency_score": 0.0,
  "consecutive_misses": 0,
  "failure_rate": 0.0,
  "created_at": "2024-01-01T00:00:00"
}
```

### List Habits

**GET** `/api/habits?status=active`

Query parameters:
- `status` (optional): Filter by status (active, paused, archived, at_risk)

Response: `200 OK`
```json
[
  {
    "id": 1,
    "name": "Morning Exercise",
    ...
  }
]
```

### Get Habit

**GET** `/api/habits/{habit_id}`

Response: `200 OK`
```json
{
  "id": 1,
  "name": "Morning Exercise",
  ...
}
```

### Update Habit

**PUT** `/api/habits/{habit_id}`

Request body (all fields optional):
```json
{
  "name": "Updated Name",
  "status": "paused"
}
```

Response: `200 OK`
```json
{
  "id": 1,
  "name": "Updated Name",
  ...
}
```

### Delete Habit

**DELETE** `/api/habits/{habit_id}`

Response: `204 No Content`

## Habit Logs

### Log Habit

**POST** `/api/habit-logs`

Request body:
```json
{
  "habit_id": 1,
  "log_date": "2024-01-01",
  "status": "done",
  "notes": "Completed successfully"
}
```

Status values: `done`, `skipped`, `missed`

Response: `201 Created`
```json
{
  "id": 1,
  "habit_id": 1,
  "log_date": "2024-01-01",
  "status": "done",
  "notes": "Completed successfully",
  "created_at": "2024-01-01T00:00:00"
}
```

### Get Habit Logs

**GET** `/api/habit-logs/habit/{habit_id}?start_date=2024-01-01&end_date=2024-01-31`

Query parameters:
- `start_date` (optional): Filter logs from this date
- `end_date` (optional): Filter logs until this date

Response: `200 OK`
```json
[
  {
    "id": 1,
    "habit_id": 1,
    "log_date": "2024-01-01",
    "status": "done",
    "notes": null,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

## Goals

### Create Goal

**POST** `/api/goals`

Request body:
```json
{
  "name": "Run 100 Miles",
  "description": "Run 100 miles this month",
  "target_value": 100,
  "unit": "miles",
  "habit_ids": [1, 2],
  "contribution_weights": [1.0, 0.5]
}
```

Response: `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Run 100 Miles",
  "description": "Run 100 miles this month",
  "target_value": 100,
  "current_value": 0,
  "unit": "miles",
  "is_completed": false,
  "created_at": "2024-01-01T00:00:00",
  "habit_contributions": [
    {
      "habit_id": 1,
      "habit_name": "Morning Exercise",
      "contribution_weight": 1.0
    }
  ]
}
```

### List Goals

**GET** `/api/goals`

Response: `200 OK`
```json
[
  {
    "id": 1,
    "name": "Run 100 Miles",
    ...
  }
]
```

### Get Goal

**GET** `/api/goals/{goal_id}`

Response: `200 OK`
```json
{
  "id": 1,
  "name": "Run 100 Miles",
  ...
}
```

### Update Goal

**PUT** `/api/goals/{goal_id}`

Request body (all fields optional):
```json
{
  "name": "Updated Goal Name",
  "target_value": 150
}
```

Response: `200 OK`

### Delete Goal

**DELETE** `/api/goals/{goal_id}`

Response: `204 No Content`

## Analytics

### Dashboard Stats

**GET** `/api/analytics/dashboard`

Response: `200 OK`
```json
{
  "total_habits": 5,
  "active_habits": 4,
  "at_risk_habits": 1,
  "total_streak": 45,
  "average_consistency": 75.5,
  "today_completions": 3
}
```

### Habit Heatmap

**GET** `/api/analytics/habits/{habit_id}/heatmap?year=2024`

Query parameters:
- `year` (optional): Year for heatmap (default: current year)

Response: `200 OK`
```json
{
  "year": 2024,
  "data": {
    "2024-01-01": 1,
    "2024-01-02": 1,
    "2024-01-03": 0
  }
}
```

### Weekly Stats

**GET** `/api/analytics/habits/{habit_id}/weekly`

Response: `200 OK`
```json
{
  "week_start": "2024-01-01",
  "week_end": "2024-01-07",
  "stats": {
    "done": 5,
    "skipped": 1,
    "missed": 1
  }
}
```

### Monthly Stats

**GET** `/api/analytics/habits/{habit_id}/monthly?year=2024&month=1`

Query parameters:
- `year` (optional): Year (default: current year)
- `month` (optional): Month 1-12 (default: current month)

Response: `200 OK`
```json
{
  "year": 2024,
  "month": 1,
  "month_start": "2024-01-01",
  "month_end": "2024-01-31",
  "stats": {
    "done": 20,
    "skipped": 5,
    "missed": 6
  }
}
```

### Consistency Trend

**GET** `/api/analytics/habits/{habit_id}/consistency-trend?days=30`

Query parameters:
- `days` (optional): Number of days (default: 30)

Response: `200 OK`
```json
{
  "habit_id": 1,
  "days": 30,
  "trend": [
    {
      "date": "2024-01-01",
      "completions": 1
    },
    {
      "date": "2024-01-02",
      "completions": 1
    }
  ]
}
```

## Suggestions

### Get Adaptive Suggestions

**GET** `/api/suggestions/habits/{habit_id}/adaptive`

Response: `200 OK`
```json
{
  "habit_id": 1,
  "suggestions": {
    "reduce_frequency": {
      "current": "daily",
      "suggested": "weekly",
      "reason": "High failure rate (55.0%). Consider reducing frequency."
    },
    "reduce_difficulty": {
      "current": "hard",
      "suggested": "easy",
      "reason": "Low consistency score (25.0%). Consider making the habit easier."
    }
  }
}
```

### Detect Risks

**POST** `/api/suggestions/detect-risks`

Response: `200 OK`
```json
{
  "at_risk_count": 2,
  "habits": [
    {
      "id": 1,
      "name": "Morning Exercise"
    },
    {
      "id": 3,
      "name": "Meditation"
    }
  ]
}
```

## WebSocket

### Connect

**WS** `/ws?token={jwt_token}`

Connection:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_JWT_TOKEN');
```

### Event Types

#### Connected
```json
{
  "type": "connected",
  "data": {
    "message": "WebSocket connected",
    "user_id": 1
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

#### Habit Logged
```json
{
  "type": "habit_logged",
  "data": {
    "habit_id": 1,
    "habit_name": "Morning Exercise",
    "log_date": "2024-01-01",
    "status": "done",
    "streak": 5
  },
  "user_id": 1,
  "timestamp": "2024-01-01T00:00:00"
}
```

#### Habit At Risk
```json
{
  "type": "habit_at_risk",
  "data": {
    "habit_id": 1,
    "habit_name": "Morning Exercise",
    "consecutive_misses": 2
  },
  "user_id": 1,
  "timestamp": "2024-01-01T00:00:00"
}
```

#### Goal Completed
```json
{
  "type": "goal_completed",
  "data": {
    "goal_id": 1,
    "goal_name": "Run 100 Miles",
    "current_value": 100,
    "target_value": 100
  },
  "user_id": 1,
  "timestamp": "2024-01-01T00:00:00"
}
```

#### Nudge
```json
{
  "type": "nudge",
  "data": {
    "message": "You have 2 inactive habits",
    "habits": [
      {"id": 1, "name": "Morning Exercise"},
      {"id": 3, "name": "Meditation"}
    ]
  },
  "user_id": 1,
  "timestamp": "2024-01-01T00:00:00"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently not implemented. Consider adding rate limiting for production:
- 100 requests per minute per IP
- 10 requests per minute per authenticated user

## Pagination

Currently not implemented. For large datasets, consider adding:
- `page` query parameter
- `limit` query parameter
- Response includes `total`, `page`, `limit`, `pages`

## Filtering and Sorting

Currently basic filtering available. Consider adding:
- Sort by date, name, streak, etc.
- Filter by date ranges
- Search by name/description

