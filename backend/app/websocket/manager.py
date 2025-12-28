from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket
import json
import asyncio
from app.core.redis_client import get_redis_client


class ConnectionManager:
    """
    Manages WebSocket connections per user.
    Supports multiple connections per user (e.g., multiple browser tabs).
    """
    
    def __init__(self):
        # Map user_id -> Set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.redis_client = get_redis_client()
        self.pubsub = None
        self._listening = False
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a WebSocket for a user"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        
        # Start listening to Redis pub/sub if not already started
        if not self._listening:
            asyncio.create_task(self._listen_to_redis())
            self._listening = True
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a WebSocket for a user"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def broadcast_to_user(self, user_id: int, event_type: str, data: dict):
        """Broadcast an event to a user's connections"""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": str(datetime.utcnow().isoformat())
        }
        await self.send_personal_message(message, user_id)
    
    async def _listen_to_redis(self):
        """Listen to Redis pub/sub and forward messages to WebSocket connections"""
        self.pubsub = self.redis_client.pubsub()
        
        # Subscribe to user-specific channels
        # In production, you might want to subscribe to a pattern like "user:*"
        # For now, we'll handle this in the handlers
        
        while True:
            try:
                message = self.pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    try:
                        event = json.loads(message['data'])
                        user_id = event.get('user_id')
                        if user_id:
                            await self.broadcast_to_user(
                                user_id,
                                event.get('type', 'notification'),
                                event.get('data', {})
                            )
                    except Exception as e:
                        print(f"Error processing Redis message: {e}")
                
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error in Redis listener: {e}")
                await asyncio.sleep(1)
    
    async def subscribe_to_user_channel(self, user_id: int):
        """Subscribe to Redis channel for a specific user"""
        if self.pubsub:
            channel = f"user:{user_id}"
            self.pubsub.subscribe(channel)


# Global connection manager instance
manager = ConnectionManager()

