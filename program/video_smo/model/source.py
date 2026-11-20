"""Source — infinite camera (ИБ) with Uniform inter-arrival (ИЗ2)."""

from __future__ import annotations
from typing import Optional

from smo.laws.random_law import RandomLaw
from smo.model.request import Request


class Source:
    def __init__(self, source_id: int, interarrival_law: RandomLaw) -> None:
        self.id = source_id
        self._law = interarrival_law
        self.seq = 0
        self.generated = 0
        self.next_arrival: float = 0.0

    def generate(self, now: float) -> Request:
        self.seq += 1
        self.generated += 1
        return Request(source_id=self.id, seq=self.seq, created_at=now)

    def schedule_next(self, now: float) -> float:
        self.next_arrival = now + self._law.sample()
        return self.next_arrival

    def __repr__(self) -> str:
        return (
            f"Source({self.id}: next={self.next_arrival:.3f}, "
            f"gen={self.generated}, law={self._law})"
        )
