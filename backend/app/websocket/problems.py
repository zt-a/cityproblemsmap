# app/websocket/problems.py
from fastapi import WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
import asyncio
import json
import logging

from app.database import get_db
from app.models.problem import Problem
from app.services.auth import decode_token
from app.services.redis_client import redis_client

logger = logging.getLogger(__name__)


async def websocket_problem(
    websocket: WebSocket,
    problem_id: int,
    token: str = Query(None, description="JWT access token (optional)"),
    db: Session = Depends(get_db),
):
    """
    WebSocket для конкретной проблемы.

    События:
    - comment_added: Новый комментарий
    - vote_changed: Изменился счет голосов
    - status_updated: Статус изменился
    - media_added: Добавлено фото/видео
    - problem_updated: Обновление данных проблемы

    Не требует авторизации - любой может подписаться на обновления проблемы.

    Использование:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/problems/123');

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Problem update:', data);
    };
    ```
    """
    # Проверить что проблема существует
    problem = db.query(Problem).filter_by(entity_id=problem_id, is_current=True).first()
    if not problem:
        await websocket.close(code=1008, reason="Problem not found")
        return

    # Опционально верифицировать токен (для персонализации)
    user_id = None
    if token:
        try:
            payload = decode_token(token)
            user_id = int(payload["sub"])
        except:
            pass


    # ✅ Закрыть сессию до входа в цикл
    db.close()
    
    await websocket.accept()

    try:
        # Подписаться на Redis pub/sub для этой проблемы
        pubsub = redis_client.pubsub()
        channel_name = f"problem:{problem_id}"
        pubsub.subscribe(channel_name)

        logger.info(f"Client subscribed to problem {problem_id} (user_id={user_id})")

        # Отправить приветственное сообщение
        await websocket.send_json({
            "type": "connected",
            "message": f"Connected to problem {problem_id}",
            "problem_id": problem_id,
        })

        # Слушать сообщения из Redis
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)

            if message and message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    await websocket.send_json(data)
                    logger.debug(f"Sent update for problem {problem_id}: {data.get('type')}")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in Redis message: {e}")
                except Exception as e:
                    logger.error(f"Error sending update: {e}")

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from problem {problem_id}")
    except Exception as e:
        logger.error(f"WebSocket error for problem {problem_id}: {e}")
    finally:
        try:
            pubsub.unsubscribe(channel_name)
            pubsub.close()
        except:
            pass
