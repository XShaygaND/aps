"""
Selection dispatcher (ДВ).

Д2Б2 — choose request from buffer by LIFO
Д2П2 — choose free device by ring
"""

from __future__ import annotations
from typing import Callable, Optional

from smo.model.buffer import Buffer
from smo.model.device import DevicePool
from smo.model.request import Request
from smo.events.event_calendar import EventCalendar
from smo.events.event_type import EventType


class SelectionDispatcher:
    def __init__(
        self,
        buffer: Buffer,
        pool: DevicePool,
        calendar: EventCalendar,
    ) -> None:
        self._buffer = buffer
        self._pool = pool
        self._calendar = calendar

    def dispatch(self, now: float) -> None:
        """
        While there is a free device and a waiting request:
          assign LIFO request to ring-chosen device and schedule COMPLETION.
        """
        while True:
            dev_id = self._pool.find_free_by_ring()
            if dev_id is None:
                break
            req = self._buffer.extract_lifo()
            if req is None:
                break
            finish = self._pool.start(dev_id, req, now)
            self._calendar.add(
                EventType.COMPLETION,
                finish,
                device_id=dev_id,
            )
