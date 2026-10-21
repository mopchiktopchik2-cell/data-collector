import asyncio
import logging

from messaging.message import Message


class MessageQueue:
    def __init__(self, maxsize: int) -> None:
        self._queue: asyncio.Queue[Message] = asyncio.Queue(maxsize=maxsize)
        self._log = logging.getLogger("QUEUE")
        self.dropped = 0

    async def put(self, message: Message) -> bool:
        try:
            self._queue.put_nowait(message)
        except asyncio.QueueFull:
            self.dropped += 1
            self._log.warning(
                "[QUEUE] Full (size=%d). Dropped message from %s. Total dropped: %d",
                self._queue.qsize(), message.device_id, self.dropped,
            )
            return False
        self._log.info("[QUEUE] Message added. Queue size: %d", self._queue.qsize())
        return True

    async def get(self) -> Message:
        message = await self._queue.get()
        self._log.info("[QUEUE] Message taken. Queue size: %d", self._queue.qsize())
        return message

    def task_done(self) -> None:
        self._queue.task_done()

    async def join(self) -> None:
        await self._queue.join()

    def qsize(self) -> int:
        return self._queue.qsize()

    @property
    def maxsize(self) -> int:
        return self._queue.maxsize