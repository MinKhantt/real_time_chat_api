import asyncio
import json
from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket

from app.core.redis import redis_client


class ConnectionManager:
    def __init__(self) -> None:
        self._active_connections: Dict[UUID, Set[WebSocket]] = {}
        self._redis_tasks: Dict[UUID, asyncio.Task] = {}
        self._redis_pubsubs = {}
        self._lock = asyncio.Lock()

    async def connect(self, conversation_id: UUID, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._active_connections.setdefault(conversation_id, set())
            connections.add(websocket)
            if conversation_id not in self._redis_tasks:
                await self._start_redis_listener(conversation_id)

    async def disconnect(self, conversation_id: UUID, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._active_connections.get(conversation_id)
            if connections and websocket in connections:
                connections.remove(websocket)

            if not connections:
                self._active_connections.pop(conversation_id, None)
                await self._stop_redis_listener(conversation_id)

    async def broadcast(self, conversation_id: UUID, payload) -> None:
        if isinstance(payload, str):
            payload = json.loads(payload)

        connections = list(self._active_connections.get(conversation_id, set()))
        if not connections:
            return

        for websocket in connections:
            try:
                await websocket.send_json(payload)
            except Exception:
                await self.disconnect(conversation_id, websocket)

    async def _start_redis_listener(self, conversation_id: UUID) -> None:
        channel = self._channel_name(conversation_id)
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)
        self._redis_pubsubs[conversation_id] = pubsub
        self._redis_tasks[conversation_id] = asyncio.create_task(
            self._redis_listen_loop(conversation_id, pubsub)
        )

    async def _stop_redis_listener(self, conversation_id: UUID) -> None:
        task = self._redis_tasks.pop(conversation_id, None)
        pubsub = self._redis_pubsubs.pop(conversation_id, None)

        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        if pubsub:
            channel = self._channel_name(conversation_id)
            await pubsub.unsubscribe(channel)
            await pubsub.close()

    async def _redis_listen_loop(self, conversation_id: UUID, pubsub) -> None:
        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                await self.broadcast(conversation_id, message.get("data"))
        except asyncio.CancelledError:
            pass

    def _channel_name(self, conversation_id: UUID) -> str:
        return f"conversation:{conversation_id}"


ws_manager = ConnectionManager()
