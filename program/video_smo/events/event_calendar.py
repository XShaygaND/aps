"""Priority queue of future events (special-states principle)."""

from __future__ import annotations
import heapq
from typing import List, Optional

from smo.events.event import Event
from smo.events.event_type import EventType


class EventCalendar:
    def __init__(self) -> None:
        self._heap: List[Event] = []
        self._seq = 0

    def add(
        self,
        etype: EventType,
        time: float,
        source_id: Optional[int] = None,
        device_id: Optional[int] = None,
    ) -> None:
        self._seq += 1
        heapq.heappush(
            self._heap,
            Event(
                time=time,
                seq=self._seq,
                type=etype,
                source_id=source_id,
                device_id=device_id,
            ),
        )

    def next(self) -> Optional[Event]:
        if not self._heap:
            return None
        return heapq.heappop(self._heap)

    def is_empty(self) -> bool:
        return not self._heap

    def __len__(self) -> int:
        return len(self._heap)
