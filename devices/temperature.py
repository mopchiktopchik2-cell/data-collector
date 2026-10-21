import random

from devices.base import BaseDevice


class TemperatureDevice(BaseDevice):
    device_type = "temperature"
    unit = "C"

    def generate_value(self) -> float:
        return round(random.uniform(-30.0, 45.0), 2)