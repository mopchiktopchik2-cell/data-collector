import random

from devices.base import BaseDevice


class PressureDevice(BaseDevice):
    device_type = "pressure"
    unit = "hPa"

    def generate_value(self) -> float:
        return round(random.uniform(950.0, 1050.0), 2)