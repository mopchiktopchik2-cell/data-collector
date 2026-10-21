import asyncio
import logging
import math
from datetime import datetime, timezone

from messaging.message import Message
from messaging.message_queue import MessageQueue
from stats import Stats
from storage.database import Database


class Processor:
    def __init__(self, queue: MessageQueue, database: Database, stats: Stats) -> None:
        self.queue = queue
        self.database = database
        self.stats = stats
        self._log = logging.getLogger("PROCESSOR")

    @staticmethod
    def validate(message: Message) -> None:
        if not isinstance(message, Message):
            raise ValueError("not a Message instance")
        if not message.device_id or not isinstance(message.device_id, str):
            raise ValueError("invalid device_id")
        if not message.device_type or not isinstance(message.device_type, str):
            raise ValueError("invalid device_type")
        if not isinstance(message.value, (int, float)) or isinstance(message.value, bool):
            raise ValueError("value is not numeric")
        if isinstance(message.value, float) and (math.isnan(message.value) or math.isinf(message.value)):
            raise ValueError("value is NaN/Inf")
        try:
            datetime.fromisoformat(message.timestamp)
        except (TypeError, ValueError):
            raise ValueError("invalid timestamp")

    async def run(self) -> None:
        while True:
            message = await self.queue.get()
            self.stats.inc_received()
            try:
                self.validate(message)
                self._log.info("[PROCESSOR] Processing message from %s", message.device_id)
                message.processed_at = datetime.now(timezone.utc).isoformat()
                await self.database.save(message)
                self.stats.record(message)
                self.stats.inc_processed()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.stats.inc_error()
                self._log.error(
                    "[PROCESSOR] Failed message from %s: %s",
                    getattr(message, "device_id", "?"), exc,
                )
            finally:
                self.queue.task_done()