"""
Buffer — ring buffer for variant 16.

Д1ОЗ1 — fill by ring (write pointer)
Д1ОО3 — on overflow drop the oldest
Д2Б2  — extract by LIFO (newest first)
"""

from __future__ import annotations
from typing import List, Optional

from smo.model.request import Request


class Buffer:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("buffer capacity must be >= 1")
        self.capacity = capacity
        self.slots: List[Optional[Request]] = [None] * capacity
        self.write_ptr: int = 0

    def __len__(self) -> int:
        return sum(1 for s in self.slots if s is not None)

    def is_full(self) -> bool:
        return len(self) == self.capacity

    def is_empty(self) -> bool:
        return len(self) == 0

    def find_free_by_ring(self) -> Optional[int]:
        """Д1ОЗ1: walk from write_ptr looking for a free slot."""
        for i in range(self.capacity):
            idx = (self.write_ptr + i) % self.capacity
            if self.slots[idx] is None:
                return idx
        return None

    def put(self, request: Request, index: int) -> None:
        if self.slots[index] is not None:
            raise RuntimeError(f"slot {index} is occupied")
        self.slots[index] = request
        self.write_ptr = (index + 1) % self.capacity

    def evict_oldest(self) -> Request:
        """Д1ОО3: remove request with smallest (created_at, source_id, seq)."""
        oldest: Optional[Request] = None
        oldest_idx = -1
        for i, r in enumerate(self.slots):
            if r is None:
                continue
            key = (r.created_at, r.source_id, r.seq)
            if oldest is None or key < (oldest.created_at, oldest.source_id, oldest.seq):
                oldest = r
                oldest_idx = i
        if oldest is None:
            raise RuntimeError("evict_oldest called on empty buffer")
        self.slots[oldest_idx] = None
        return oldest

    def extract_lifo(self) -> Optional[Request]:
        """Д2Б2: remove newest request (largest created_at, source_id, seq)."""
        newest: Optional[Request] = None
        newest_idx = -1
        for i, r in enumerate(self.slots):
            if r is None:
                continue
            key = (r.created_at, r.source_id, r.seq)
            if newest is None or key > (newest.created_at, newest.source_id, newest.seq):
                newest = r
                newest_idx = i
        if newest is None:
            return None
        self.slots[newest_idx] = None
        return newest

    def snapshot(self) -> List[Optional[str]]:
        return [r.id if r is not None else None for r in self.slots]

    def __repr__(self) -> str:
        cells = []
        for i, r in enumerate(self.slots):
            mark = "*" if i == self.write_ptr else " "
            cells.append(f"{mark}{r.id if r else '·':>6}")
        return (
            f"Buffer[{','.join(cells)}]  "
            f"(ptr→{self.write_ptr}, {len(self)}/{self.capacity})"
        )
