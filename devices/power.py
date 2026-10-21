import random

from devices.base import BaseDevice


class PowerDevice(BaseDevice):
    device_type = "power"
    unit = "W"

    def generate_value(self) -> float:
        return round(random.uniform(0.0, 5000.0), 2)