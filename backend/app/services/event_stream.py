import asyncio
import json
import logging
from typing import Dict, Set, Any

logger = logging.getLogger("mediscan.services.event_stream")

class EventStreamManager:
    """Manages Server-Sent Events (SSE) queues for active research queries."""

    def __init__(self):
        # Maps query_id -> set of asyncio.Queue instances
        self.subscribers: Dict[str, Set[asyncio.Queue]] = {}

    def subscribe(self, query_id: str) -> asyncio.Queue:
        """Subscribe a client connection to receive events for query_id."""
        queue: asyncio.Queue = asyncio.Queue()
        if query_id not in self.subscribers:
            self.subscribers[query_id] = set()
        self.subscribers[query_id].add(queue)
        logger.info(f"Subscribed to query {query_id}. Active subscribers: {len(self.subscribers[query_id])}")
        return queue

    def unsubscribe(self, query_id: str, queue: asyncio.Queue):
        """Unsubscribe a client queue."""
        if query_id in self.subscribers and queue in self.subscribers[query_id]:
            self.subscribers[query_id].remove(queue)
            if not self.subscribers[query_id]:
                del self.subscribers[query_id]
        logger.info(f"Unsubscribed from query {query_id}")

    async def publish(self, query_id: str, event_type: str, data: Dict[str, Any]):
        """Publish an event to all active listeners for query_id."""
        if query_id not in self.subscribers:
            return

        payload = {
            "event": event_type,
            "data": data
        }
        dead_queues = set()
        for queue in self.subscribers[query_id]:
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                dead_queues.add(queue)
            except Exception as e:
                logger.error(f"Error publishing to subscriber queue: {e}")
                dead_queues.add(queue)

        for q in dead_queues:
            self.unsubscribe(query_id, q)

event_stream_manager = EventStreamManager()
