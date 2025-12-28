# Database Migration Guide - Gamification Features

## Quick Migration

Run these commands to add gamification fields to your database:

```bash
cd backend
source venv/bin/activate

# Create migration
alembic revision --autogenerate -m "Add gamification fields"

# Apply migration
alembic upgrade head

# Initialize achievements (run once)
python -c "
from app.database import SessionLocal
from app.services.gamification_service import GamificationService
db = SessionLocal()
GamificationService.initialize_achievements(db)
print('✅ Achievements initialized!')
"
```

## What Gets Added

### New Tables:
- `achievements` - Available achievement definitions
- `user_achievements` - User's unlocked achievements

### New Columns in `users`:
- `total_xp` (Integer, default: 0)
- `level` (Integer, default: 1)
- `total_points` (Integer, default: 0)

## Verify Migration

```bash
# Check if tables exist
psql -U smarthabit -d smarthabit_db -c "\dt"

# Check if user has new columns
psql -U smarthabit -d smarthabit_db -c "\d users"
```

## After Migration

1. **Restart backend** (if needed)
2. **Refresh frontend** - should auto-reload
3. **Complete a habit** - you'll see XP notifications!
4. **Check dashboard** - see your level and XP

## Troubleshooting

If migration fails:
```bash
# Check current migration status
alembic current

# If needed, manually add columns
psql -U smarthabit -d smarthabit_db -c "
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_xp INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 1;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_points INTEGER DEFAULT 0;
"
```

