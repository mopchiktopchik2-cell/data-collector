from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Message:
    device_id: str
    device_type: str
    timestamp: str
    value: float
    unit: str
    processed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)