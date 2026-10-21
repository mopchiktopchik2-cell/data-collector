import asyncio
import logging
import signal

import config
from devices.base import BaseDevice
from devices.humidity import HumidityDevice
from devices.power import PowerDevice
from devices.pressure import PressureDevice
from devices.temperature import TemperatureDevice
from messaging.message_queue import MessageQueue
from processing.processor import Processor
from stats import Stats
from storage.database import Database


log = logging.getLogger("MAIN")

DEVICE_CLASSES = [
    ("temperature", TemperatureDevice),
    ("humidity", HumidityDevice),
    ("pressure", PressureDevice),
    ("power", PowerDevice),
]


def build_devices(queue: MessageQueue) -> list[BaseDevice]:
    devices: list[BaseDevice] = []
    for i in range(config.NUM_DEVICES):
        type_name, cls = DEVICE_CLASSES[i % len(DEVICE_CLASSES)]
        devices.append(
            cls(
                device_id=f"{type_name}_{i:02d}",
                interval=config.DEVICE_INTERVALS[type_name],
                queue=queue,
            )
        )
    return devices


async def stats_loop(stats: Stats, queue: MessageQueue, shutdown: asyncio.Event) -> None:
    while True:
        try:
            await asyncio.wait_for(shutdown.wait(), timeout=config.STATS_INTERVAL)
            return
        except asyncio.TimeoutError:
            stats.log_report(queue)


def _install_signal_handlers(shutdown: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()

    def handler(signum, frame):
        loop.call_soon_threadsafe(shutdown.set)

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, handler)
        except (ValueError, OSError):
            pass


async def run() -> None:
    queue = MessageQueue(maxsize=config.QUEUE_MAXSIZE)
    database = Database(config.DB_PATH)
    await database.connect()

    stats = Stats()
    processor = Processor(queue=queue, database=database, stats=stats)
    devices = build_devices(queue)

    shutdown = asyncio.Event()
    _install_signal_handlers(shutdown)

    processor_task = asyncio.create_task(processor.run(), name="processor")
    device_tasks = [asyncio.create_task(d.run(), name=d.device_id) for d in devices]
    stats_task = asyncio.create_task(stats_loop(stats, queue, shutdown), name="stats")

    log.info(
        "Started: devices=%d, queue_maxsize=%d, run_time=%s",
        len(devices), config.QUEUE_MAXSIZE, config.RUN_TIME,
    )

    try:
        if config.RUN_TIME is not None:
            try:
                await asyncio.wait_for(shutdown.wait(), timeout=config.RUN_TIME)
            except asyncio.TimeoutError:
                pass
        else:
            await shutdown.wait()
    finally:
        log.info("Shutdown: stopping devices...")
        for d in devices:
            d.stop()
        for t in device_tasks:
            t.cancel()
        results = await asyncio.gather(*device_tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, BaseException) and not isinstance(r, asyncio.CancelledError):
                log.error("Device task failed: %r", r)

        log.info("Draining queue (remaining=%d)...", queue.qsize())
        try:
            await asyncio.wait_for(queue.join(), timeout=config.SHUTDOWN_DRAIN_TIMEOUT)
        except asyncio.TimeoutError:
            log.warning("Drain timeout: %d messages left", queue.qsize())

        processor_task.cancel()
        await asyncio.gather(processor_task, return_exceptions=True)

        stats_task.cancel()
        await asyncio.gather(stats_task, return_exceptions=True)

        await database.close()

        log.info("Final statistics:")
        stats.log_report(queue)


def main() -> None:
    logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()