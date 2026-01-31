import asyncio
from typing import Any, Dict, Optional
from fog.models.task import TaskPacket
from fog.core.logging import logger

class TaskQueue:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def enqueue(self, task: TaskPacket):
        await self.queue.put(task)
        logger.info("TASK_ENQUEUED", {"task_id": task.task_id})

    async def dequeue(self) -> TaskPacket:
        task = await self.queue.get()
        return task

    def task_done(self):
        self.queue.task_done()

    def size(self) -> int:
        return self.queue.qsize()

# Global task queue instance
task_queue = TaskQueue()
