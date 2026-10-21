import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from messaging.message import Message
from messaging.message_queue import MessageQueue


class BaseDevice(ABC):
    device_type: str = "base"
    unit: str = ""

    def __init__(self, device_id: str, interval: float, queue: MessageQueue) -> None:
        self.device_id = device_id
        self.interval = interval
        self.queue = queue
        self._log = logging.getLogger("DEVICE")
        self._stopped = asyncio.Event()

    @abstractmethod
    def generate_value(self) -> float: ...

    def _build_message(self) -> Message:
        return Message(
            device_id=self.device_id,
            device_type=self.device_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            value=self.generate_value(),
            unit=self.unit,
        )

    def stop(self) -> None:
        self._stopped.set()

    async def run(self) -> None:
        while not self._stopped.is_set():
            try:
                message = self._build_message()
                self._log.info(
                    "[DEVICE] %s generated: %s %s",
                    self.device_id, message.value, message.unit,
                )
                await self.queue.put(message)
            except asyncio.CancelledError:
                raise
            except Exception:
                self._log.exception("[DEVICE] %s loop error, continuing", self.device_id)

            try:
                await asyncio.wait_for(self._stopped.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                pass