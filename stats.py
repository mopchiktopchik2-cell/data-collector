import logging
import statistics
from collections import defaultdict

from messaging.message import Message
from messaging.message_queue import MessageQueue


class Stats:
    def __init__(self) -> None:
        self.received = 0
        self.processed = 0
        self.errors = 0
        self.per_device: dict[str, int] = defaultdict(int)
        self.values: dict[str, list[float]] = defaultdict(list)
        self._log = logging.getLogger("STATS")

    def inc_received(self) -> None:
        self.received += 1

    def inc_processed(self) -> None:
        self.processed += 1

    def inc_error(self) -> None:
        self.errors += 1

    def record(self, message: Message) -> None:
        self.per_device[message.device_id] += 1
        self.values[message.device_type].append(message.value)

    def log_report(self, queue: MessageQueue) -> None:
        self._log.info(
            "[STATS] Received: %d | Processed: %d | Errors: %d | Queue: %d | Dropped: %d",
            self.received, self.processed, self.errors, queue.qsize(), queue.dropped,
        )
        for device_id, count in sorted(self.per_device.items()):
            self._log.info("[STATS]   %s: %d", device_id, count)
        for device_type, vals in sorted(self.values.items()):
            if not vals:
                continue
            self._log.info(
                "[STATS]   %s: n=%d avg=%.2f min=%.2f max=%.2f",
                device_type, len(vals), statistics.fmean(vals),
                min(vals), max(vals),
            )