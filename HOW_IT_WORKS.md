# How Each Page Works - Complete Guide

## Example: Creating "DSA" Habit
**Habit Name:** DSA (Data Structures and Algorithms)  
**Description:** Solve 4-5 DSA questions daily  
**Frequency:** Daily  
**Difficulty:** Medium  
**Priority:** High

---

## 1. **Registration/Login Page** (`/register` and `/login`)

### How It Works:
1. **User enters credentials:**
   - Email: `user@example.com`
   - Password: `password123`
   - Full Name: `John Doe`

2. **Registration Flow:**
   ```
   Frontend → POST /api/auth/register
   Backend → Creates user in PostgreSQL
   Backend → Returns user object
   Frontend → Auto-login → Redirects to Dashboard
   ```

3. **Login Flow:**
   ```
   Frontend → POST /api/auth/login (FormData: username, password)
   Backend → Validates credentials → Returns JWT token
   Frontend → Stores token in localStorage
   Frontend → Redirects to Dashboard
   ```

### Attributes:
- **Email**: Unique identifier
- **Password**: Hashed with bcrypt
- **Full Name**: Optional display name
- **JWT Token**: Stored in localStorage for authentication

---

## 2. **Dashboard Page** (`/`)

### How It Works:
1. **On Load:**
   ```
   Frontend → GET /api/analytics/dashboard
   Backend → Calculates stats from database
   Returns: {
     total_habits: 5,
     active_habits: 4,
     at_risk_habits: 1,
     total_streak: 45,
     average_consistency: 75.5,
     today_completions: 3
   }
   ```

2. **WebSocket Connection:**
   ```
   Frontend → Connects to ws://localhost:8000/ws?token=JWT
   Backend → Subscribes to user-specific Redis channel
   Real-time events: habit_logged, habit_at_risk, goal_completed, nudge
   ```

3. **Real-Time Updates:**
   - When you log a habit → WebSocket sends `habit_logged` event
   - Dashboard updates streak instantly
   - Shows notifications for at-risk habits

### Example with DSA Habit:
- **Total Habits**: 5 (including DSA)
- **Active Habits**: 4 (DSA is active)
- **Today's Completions**: 1 (if you logged DSA today)
- **Total Streak**: 45 days (sum of all habit streaks)

---

## 3. **Habits Page** (`/habits`)

### Creating "DSA" Habit:

#### Step 1: Fill Form
```
Name: "DSA"
Description: "Solve 4-5 DSA questions daily"
Frequency: "daily"
Difficulty: "medium"
Priority: "high"
```

#### Step 2: Submit
```
Frontend → POST /api/habits
Body: {
  "name": "DSA",
  "description": "Solve 4-5 DSA questions daily",
  "frequency": "daily",
  "difficulty": "medium",
  "priority": "high"
}
```

#### Step 3: Backend Processing
```
Backend → Creates Habit record in PostgreSQL:
- user_id: 1 (your user ID)
- name: "DSA"
- frequency: "daily"
- difficulty: "medium"
- priority: "high"
- status: "active"
- current_streak: 0
- consistency_score: 0.0
```

#### Step 4: Response
```
Backend → Returns habit object with ID
Frontend → Adds to habits list
Frontend → Shows habit card
```

### Habit Card Display:
```
┌─────────────────────────────────┐
│ DSA                    [active] │
│ Solve 4-5 DSA questions daily   │
│                                  │
│ Streak: 0 days                   │
│ Consistency: 0.0%                │
│                                  │
│ [✓ Done]  [Skip]                 │
└─────────────────────────────────┘
```

### Logging Habit (Daily):

#### When You Click "✓ Done":
```
Frontend → POST /api/habit-logs
Body: {
  "habit_id": 1,
  "log_date": "2024-12-28",
  "status": "done",
  "notes": null
}
```

#### Backend Processing:
1. **Creates Log:**
   ```
   habit_logs table:
   - habit_id: 1
   - log_date: 2024-12-28
   - status: "done"
   ```

2. **Updates Habit Stats:**
   ```
   - total_completions: 0 → 1
   - current_streak: 0 → 1
   - consistency_score: 0.0 → 3.33% (1/30 days)
   - last_completed_date: 2024-12-28
   ```

3. **Checks Consecutive Misses:**
   ```
   - consecutive_misses: 0 (reset)
   - status: "active" (if was "at_risk", changes to "active")
   ```

4. **Updates Goal Progress:**
   ```
   If DSA habit contributes to a goal:
   - goal.current_value += contribution_weight
   - Checks if goal is completed
   ```

5. **Publishes Real-Time Event:**
   ```
   Redis Pub/Sub → WebSocket → Frontend
   Event: {
     "type": "habit_logged",
     "data": {
       "habit_id": 1,
       "habit_name": "DSA",
       "streak": 1
     }
   }
   ```

### After 7 Days of Logging:
```
Habit Stats:
- current_streak: 7
- longest_streak: 7
- total_completions: 7
- consistency_score: 23.33% (7/30 days)
- status: "active"
```

### If You Miss 2 Consecutive Days:
```
Day 8: Not logged → consecutive_misses: 1
Day 9: Not logged → consecutive_misses: 2

Backend (Celery job runs hourly):
- Detects 2 consecutive misses
- Updates status: "active" → "at_risk"
- Publishes event: "habit_at_risk"
- Frontend shows warning notification
```

---

## 4. **Goals Page** (`/goals`)

### Creating Goal: "Complete 100 DSA Problems"

#### Step 1: Fill Form
```
Name: "Complete 100 DSA Problems"
Description: "Solve 100 DSA questions this month"
Target Value: 100
Unit: "problems"
Habits: [DSA habit] (contributes to this goal)
Contribution Weight: 1.0 (each completion = 1 problem)
```

#### Step 2: Submit
```
Frontend → POST /api/goals
Body: {
  "name": "Complete 100 DSA Problems",
  "description": "Solve 100 DSA questions this month",
  "target_value": 100,
  "unit": "problems",
  "habit_ids": [1],  // DSA habit ID
  "contribution_weights": [1.0]
}
```

#### Step 3: Backend Processing
```
Backend → Creates Goal:
- user_id: 1
- name: "Complete 100 DSA Problems"
- target_value: 100
- current_value: 0
- is_completed: false

Backend → Creates GoalHabit relationship:
- goal_id: 1
- habit_id: 1 (DSA)
- contribution_weight: 1.0
```

### Goal Progress Tracking:

#### Every Time You Log DSA as "Done":
```
1. Habit log created
2. Goal service checks: Does this habit contribute to any goal?
3. Finds: DSA → Goal "Complete 100 DSA Problems"
4. Updates: goal.current_value += 1.0
5. Checks: current_value (7) >= target_value (100)? No
6. Goal remains incomplete
```

#### After 100 Completions:
```
goal.current_value: 100
goal.target_value: 100
is_completed: false → true
completed_at: 2024-12-28

Publishes event: "goal_completed"
Frontend shows celebration notification!
```

### Goal Display:
```
┌─────────────────────────────────┐
│ Complete 100 DSA Problems       │
│ Solve 100 DSA questions         │
│                                  │
│ ████████████░░░░░░░░  70/100    │
│                                  │
│ Contributing Habits:             │
│ - DSA (weight: 1.0)              │
└─────────────────────────────────┘
```

---

## 5. **Analytics Page** (`/analytics`)

### Weekly Stats for DSA Habit:

#### Request:
```
Frontend → GET /api/analytics/habits/1/weekly
```

#### Backend Processing:
```
1. Gets current week (Monday to Sunday)
2. Queries habit_logs for DSA habit in this week
3. Counts: done, skipped, missed
4. Returns:
   {
     "week_start": "2024-12-23",
     "week_end": "2024-12-29",
     "stats": {
       "done": 5,
       "skipped": 1,
       "missed": 1
     }
   }
```

#### Frontend Display:
```
Bar Chart:
Done:    █████ (5)
Skipped: █ (1)
Missed:  █ (1)
```

### Monthly Stats:

#### Request:
```
Frontend → GET /api/analytics/habits/1/monthly?year=2024&month=12
```

#### Response:
```
{
  "year": 2024,
  "month": 12,
  "stats": {
    "done": 20,
    "skipped": 5,
    "missed": 6
  }
}
```

### Consistency Trend (Last 30 Days):

#### Request:
```
Frontend → GET /api/analytics/habits/1/consistency-trend?days=30
```

#### Response:
```
{
  "habit_id": 1,
  "days": 30,
  "trend": [
    {"date": "2024-12-01", "completions": 1},
    {"date": "2024-12-02", "completions": 1},
    ...
    {"date": "2024-12-28", "completions": 1}
  ]
}
```

#### Frontend Display:
```
Line Chart showing daily completions over 30 days
X-axis: Dates
Y-axis: Number of completions
Shows consistency pattern
```

### Heatmap (GitHub-style):

#### Request:
```
Frontend → GET /api/analytics/habits/1/heatmap?year=2024
```

#### Response:
```
{
  "year": 2024,
  "data": {
    "2024-12-01": 1,
    "2024-12-02": 1,
    "2024-12-03": 0,  // Missed
    "2024-12-04": 1,
    ...
  }
}
```

#### Frontend Display:
```
Calendar heatmap showing:
- Green squares: Days completed
- Gray squares: Days missed
- Intensity: Based on number of completions
```

---

## 6. **Real-Time Features**

### WebSocket Events:

#### 1. Habit Logged:
```
When you click "✓ Done" on DSA:
Backend → Publishes to Redis: "user:1"
Event: {
  "type": "habit_logged",
  "data": {
    "habit_id": 1,
    "habit_name": "DSA",
    "log_date": "2024-12-28",
    "status": "done",
    "streak": 7
  }
}
Frontend → Updates dashboard stats instantly
```

#### 2. Habit At Risk:
```
After missing 2 consecutive days:
Celery job (runs hourly) → Detects risk
Backend → Updates status to "at_risk"
Publishes: {
  "type": "habit_at_risk",
  "data": {
    "habit_id": 1,
    "habit_name": "DSA",
    "consecutive_misses": 2
  }
}
Frontend → Shows warning notification
```

#### 3. Goal Completed:
```
When DSA completions reach 100:
Backend → Updates goal.is_completed = true
Publishes: {
  "type": "goal_completed",
  "data": {
    "goal_id": 1,
    "goal_name": "Complete 100 DSA Problems",
    "current_value": 100,
    "target_value": 100
  }
}
Frontend → Shows celebration message
```

#### 4. Smart Nudge:
```
If DSA habit inactive for 2+ days:
Celery job → Detects inactivity
Publishes: {
  "type": "nudge",
  "data": {
    "message": "You have 1 inactive habits",
    "habits": [{"id": 1, "name": "DSA"}]
  }
}
Frontend → Shows reminder notification
```

---

## 7. **Background Jobs (Celery)**

### Risk Detection (Runs Hourly):
```
1. Gets all active habits for all users
2. For each habit (e.g., DSA):
   - Checks last 2 days
   - If both days missing "done" → mark as "at_risk"
   - Publish alert
```

### Daily Nudges (Runs Hourly):
```
1. Gets all active habits
2. Checks: last log date < 2 days ago?
3. If yes → add to inactive list
4. If user has inactive habits:
   - Publish nudge event
   - Send email (if configured)
```

### Streak Updates (Runs Daily at Midnight):
```
1. Gets all active habits
2. Recalculates streaks
3. Updates consistency scores
4. Refreshes statistics
```

---

## Complete Flow Example: DSA Habit

### Day 1:
1. **Create Habit:**
   - Name: "DSA"
   - Frequency: Daily
   - Difficulty: Medium
   - Status: Active
   - Streak: 0

2. **Log as Done:**
   - Creates log: `{habit_id: 1, date: 2024-12-28, status: "done"}`
   - Updates: `streak: 0 → 1`, `completions: 0 → 1`
   - WebSocket: Sends `habit_logged` event
   - Dashboard: Updates instantly

### Day 2-7:
- Log "Done" each day
- Streak: 1 → 2 → 3 → 4 → 5 → 6 → 7
- Consistency: Gradually increases

### Day 8-9 (Missed):
- Day 8: Not logged → `consecutive_misses: 1`
- Day 9: Not logged → `consecutive_misses: 2`
- Celery job detects → Status: `"at_risk"`
- WebSocket: Sends `habit_at_risk` alert
- Frontend: Shows warning

### Day 10 (Resume):
- Log "Done"
- `consecutive_misses: 2 → 0`
- Status: `"at_risk" → "active"`
- Streak: Resets to 1 (broken streak)

### After 30 Days:
- Total completions: 25
- Consistency score: 83.33% (25/30)
- Longest streak: 7 days
- Current streak: 3 days

---

## Key Attributes Explained

### Habit Attributes:
- **name**: "DSA" - Display name
- **frequency**: "daily" - How often to do it
- **difficulty**: "medium" - Complexity level
- **priority**: "high" - Importance
- **status**: "active" | "paused" | "archived" | "at_risk"
- **current_streak**: Number of consecutive days completed
- **consistency_score**: Percentage (0-100) based on last 30 days
- **consecutive_misses**: Days missed in a row

### Goal Attributes:
- **target_value**: 100 - Goal to reach
- **current_value**: 25 - Current progress
- **unit**: "problems" - What you're counting
- **contribution_weight**: 1.0 - How much each habit completion counts

### Log Attributes:
- **log_date**: Date of the log entry
- **status**: "done" | "skipped" | "missed"
- **notes**: Optional notes about the session

---

## Summary

**Complete Workflow:**
1. Register/Login → Get JWT token
2. Create Habit (DSA) → Stored in database
3. Log Daily → Updates stats, triggers events
4. View Analytics → See progress, trends, heatmap
5. Create Goals → Track long-term progress
6. Real-time Updates → WebSocket notifications
7. Background Jobs → Risk detection, nudges, streak updates

Everything is connected and updates in real-time! 🚀

