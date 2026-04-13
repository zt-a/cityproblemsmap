# app/websocket/notifications.py
from fastapi import WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
import asyncio
import json
import logging

from app.database import get_db
from app.models.user import User
from app.services.auth import decode_token
from app.websocket.manager import manager
from app.services.redis_client import redis_client

logger = logging.getLogger(__name__)


async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
    db: Session = Depends(get_db),
):
    """
    WebSocket для real-time уведомлений.

    События:
    - new_comment: Новый комментарий на проблеме
    - status_changed: Статус проблемы изменился
    - new_vote: Новый голос
    - official_response: Официальный ответ
    - problem_solved: Проблема решена
    - new_follower: Новый подписчик

    Использование:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/notifications?token=YOUR_JWT_TOKEN');

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Notification:', data);
    };
    ```
    """
    # Верифицировать токен
    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except Exception as e:
        logger.error(f"WebSocket auth failed: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # Проверить что пользователь существует
    user = db.query(User).filter_by(entity_id=user_id, is_current=True).first()
    if not user:
        await websocket.close(code=1008, reason="User not found")
        return

    # ✅ Явно закрыть сессию — она больше не нужна
    db.close()

    # Подключить пользователя
    await manager.connect(user_id, websocket)

    try:
        # Подписаться на Redis pub/sub для этого пользователя
        pubsub = redis_client.pubsub()
        channel_name = f"notifications:{user_id}"
        pubsub.subscribe(channel_name)

        logger.info(f"User {user_id} subscribed to {channel_name}")

        # Отправить приветственное сообщение
        await websocket.send_json({
            "type": "connected",
            "message": "Successfully connected to notifications",
            "user_id": user_id,
        })

        # Слушать сообщения из Redis
        while True:
            # Проверяем сообщения из Redis (неблокирующий режим)
            message = pubsub.get_message(ignore_subscribe_messages=True)

            if message and message['type'] == 'message':
                try:
                    # Декодировать и отправить клиенту
                    data = json.loads(message['data'])
                    await websocket.send_json(data)
                    logger.debug(f"Sent notification to user {user_id}: {data.get('type')}")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in Redis message: {e}")
                except Exception as e:
                    logger.error(f"Error sending notification: {e}")

            # Небольшая задержка чтобы не нагружать CPU
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        # Отключить пользователя
        manager.disconnect(user_id, websocket)
        try:
            pubsub.unsubscribe(channel_name)
            pubsub.close()
        except:
            pass
