from pathlib import Path

NUM_DEVICES = 8
QUEUE_MAXSIZE = 100
STATS_INTERVAL = 5.0
RUN_TIME = 30.0
SHUTDOWN_DRAIN_TIMEOUT = 10.0

DB_PATH = Path("data_collector.db")

DEVICE_INTERVALS = {
    "temperature": 1.0,
    "humidity": 1.5,
    "pressure": 2.0,
    "power": 0.8,
}

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_LEVEL = "INFO"

LOAD_TEST = False
if LOAD_TEST:
    NUM_DEVICES = 40
    QUEUE_MAXSIZE = 200
    DEVICE_INTERVALS = {k: 0.05 for k in DEVICE_INTERVALS}
    STATS_INTERVAL = 3.0