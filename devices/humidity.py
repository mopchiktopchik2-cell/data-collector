import random

from devices.base import BaseDevice


class HumidityDevice(BaseDevice):
    device_type = "humidity"
    unit = "%"

    def generate_value(self) -> float:
        return round(random.uniform(0.0, 100.0), 2)