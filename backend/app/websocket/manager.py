# app/websocket/manager.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Менеджер WebSocket соединений.

    Управляет подключениями пользователей и отправкой сообщений.
    Поддерживает множественные соединения от одного пользователя
    (например, открыто несколько вкладок браузера).
    """

    def __init__(self):
        # user_id -> list of WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """Подключить пользователя."""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: int, websocket: WebSocket):
        """Отключить пользователя."""
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"User {user_id} disconnected. Remaining connections: {len(self.active_connections[user_id])}")

                # Удалить пользователя из словаря если нет активных соединений
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            except ValueError:
                pass

    async def send_to_user(self, user_id: int, message: dict):
        """
        Отправить сообщение конкретному пользователю.
        Отправляется во все активные соединения этого пользователя.
        """
        if user_id not in self.active_connections:
            return

        # Отправить во все соединения пользователя
        disconnected = []
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                disconnected.append(connection)

        # Удалить отключенные соединения
        for conn in disconnected:
            self.disconnect(user_id, conn)

    async def broadcast(self, message: dict, exclude_user_id: int = None):
        """
        Отправить сообщение всем подключенным пользователям.
        Опционально можно исключить конкретного пользователя.
        """
        for user_id, connections in list(self.active_connections.items()):
            if exclude_user_id and user_id == exclude_user_id:
                continue

            await self.send_to_user(user_id, message)

    def get_active_users_count(self) -> int:
        """Количество активных пользователей."""
        return len(self.active_connections)

    def get_total_connections_count(self) -> int:
        """Общее количество активных соединений."""
        return sum(len(conns) for conns in self.active_connections.values())

    def is_user_online(self, user_id: int) -> bool:
        """Проверить онлайн ли пользователь."""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# Глобальный экземпляр менеджера
manager = ConnectionManager()
