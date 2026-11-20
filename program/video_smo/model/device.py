"""
Device + DevicePool.

ПЗ1  — exponential service time (law injected)
Д2П2 — free device chosen by ring (round-robin pointer)
"""

from __future__ import annotations
from typing import List, Optional

from smo.laws.random_law import RandomLaw
from smo.model.request import Request


class Device:
    def __init__(self, device_id: int, service_law: RandomLaw) -> None:
        self.id = device_id
        self._law = service_law
        self.current: Optional[Request] = None
        self.finish_at: Optional[float] = None
        self.busy_time: float = 0.0
        self.completed: int = 0

    def is_free(self) -> bool:
        return self.current is None

    def start(self, request: Request, now: float) -> float:
        if not self.is_free():
            raise RuntimeError(f"device {self.id} is busy")
        service = self._law.sample()
        self.current = request
        self.finish_at = now + service
        request.mark_processing(now, self.id)
        return self.finish_at

    def finish(self, now: float) -> Request:
        if self.current is None or self.finish_at is None:
            raise RuntimeError(f"device {self.id} has nothing to finish")
        req = self.current
        assert req.started_at is not None
        self.busy_time += now - req.started_at
        self.completed += 1
        req.mark_completed(now)
        self.current = None
        self.finish_at = None
        return req

    def __repr__(self) -> str:
        if self.current is None:
            return f"Dev{self.id}[FREE]"
        return f"Dev{self.id}[{self.current.id}→{self.finish_at:.3f}]"


class DevicePool:
    def __init__(self, devices: List[Device]) -> None:
        self.devices = devices
        self.pointer: int = 0

    def find_free_by_ring(self) -> Optional[int]:
        """Д2П2: first free device starting from pointer (does not advance)."""
        n = len(self.devices)
        for i in range(n):
            idx = (self.pointer + i) % n
            if self.devices[idx].is_free():
                return idx
        return None

    def start(self, device_id: int, request: Request, now: float) -> float:
        finish = self.devices[device_id].start(request, now)
        self.pointer = (device_id + 1) % len(self.devices)
        return finish

    def finish(self, device_id: int, now: float) -> Request:
        return self.devices[device_id].finish(now)

    def all_free(self) -> bool:
        return all(d.is_free() for d in self.devices)

    def __repr__(self) -> str:
        parts = [repr(d) for d in self.devices]
        return f"Pool(ptr={self.pointer}) [{' | '.join(parts)}]"
