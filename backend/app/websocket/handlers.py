from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.websocket.manager import manager
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    Requires JWT token in query parameter.
    """
    # Get token from query parameters
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Authenticate user
    db = None
    try:
        db_gen = get_db()
        db = next(db_gen)
        user = await verify_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            if db:
                db.close()
            return
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        if db:
            db.close()
        return
    
    # Connect
    await manager.connect(websocket, user.id)
    await manager.subscribe_to_user_channel(user.id)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "data": {
                "message": "WebSocket connected",
                "user_id": user.id
            }
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            # For now, we just keep the connection alive
            await websocket.send_json({
                "type": "pong",
                "data": {"message": "Received"}
            })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
    finally:
        if db:
            db.close()


async def verify_token(token: str, db: Session) -> User:
    """Verify JWT token and return user"""
    from jose import JWTError, jwt
    from app.config import settings
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.email == email).first()
    return user

