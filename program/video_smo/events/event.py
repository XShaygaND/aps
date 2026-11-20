from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from smo.events.event_type import EventType


@dataclass(order=True)
class Event:
    time: float
    seq: int
    type: EventType = field(compare=False)
    source_id: Optional[int] = field(default=None, compare=False)
    device_id: Optional[int] = field(default=None, compare=False)
