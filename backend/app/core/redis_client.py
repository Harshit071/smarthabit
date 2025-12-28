import json
import redis
from datetime import datetime
from typing import Any, Dict
from app.config import settings

# Redis connection pool
redis_client = None


def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    return redis_client


def publish_event(channel: str, event_type: str, data: Dict[str, Any], user_id: int = None):
    """
    Publish an event to Redis pub/sub
    
    Args:
        channel: Redis channel name (e.g., 'user:123' for user-specific, 'global' for all)
        event_type: Type of event (e.g., 'streak_update', 'risk_alert', 'nudge')
        data: Event payload
        user_id: Optional user ID for user-specific channels
    """
    client = get_redis_client()
    event = {
        "type": event_type,
        "data": data,
        "user_id": user_id,
        "timestamp": str(datetime.utcnow().isoformat())
    }
    client.publish(channel, json.dumps(event))


def get_cache_key(key: str, user_id: int = None) -> str:
    """Generate a cache key"""
    if user_id:
        return f"user:{user_id}:{key}"
    return key


def cache_get(key: str) -> Any:
    """Get value from cache"""
    client = get_redis_client()
    value = client.get(key)
    if value:
        return json.loads(value)
    return None


def cache_set(key: str, value: Any, expire: int = 3600):
    """Set value in cache with expiration"""
    client = get_redis_client()
    client.setex(key, expire, json.dumps(value))

