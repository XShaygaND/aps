"""Request — one video frame waiting for / under analysis."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class RequestStatus(Enum):
    GENERATED = auto()
    BUFFERED = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    REJECTED = auto()


@dataclass
class Request:
    source_id: int
    seq: int
    created_at: float

    status: RequestStatus = RequestStatus.GENERATED
    buffered_at: Optional[float] = None
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    rejected_at: Optional[float] = None
    device_id: Optional[int] = None

    @property
    def id(self) -> str:
        return f"{self.source_id}.{self.seq}"

    def mark_buffered(self, t: float) -> None:
        self.status = RequestStatus.BUFFERED
        self.buffered_at = t

    def mark_processing(self, t: float, device_id: int) -> None:
        self.status = RequestStatus.PROCESSING
        self.started_at = t
        self.device_id = device_id

    def mark_completed(self, t: float) -> None:
        self.status = RequestStatus.COMPLETED
        self.finished_at = t

    def mark_rejected(self, t: float) -> None:
        self.status = RequestStatus.REJECTED
        self.rejected_at = t

    @property
    def wait_time(self) -> Optional[float]:
        if self.started_at is None:
            return None
        return self.started_at - self.created_at

    @property
    def service_time(self) -> Optional[float]:
        if self.started_at is None or self.finished_at is None:
            return None
        return self.finished_at - self.started_at

    @property
    def sojourn_time(self) -> Optional[float]:
        if self.finished_at is None:
            return None
        return self.finished_at - self.created_at
