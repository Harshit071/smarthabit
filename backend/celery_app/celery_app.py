from celery import Celery
from app.config import settings

celery_app = Celery(
    "smarthabit",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["celery_app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "daily-risk-detection": {
            "task": "celery_app.tasks.detect_habit_risks",
            "schedule": 3600.0,  # Every hour
        },
        "daily-nudges": {
            "task": "celery_app.tasks.send_daily_nudges",
            "schedule": 3600.0,  # Every hour
        },
        "update-streaks": {
            "task": "celery_app.tasks.update_all_streaks",
            "schedule": 86400.0,  # Daily at midnight
        },
    },
)

