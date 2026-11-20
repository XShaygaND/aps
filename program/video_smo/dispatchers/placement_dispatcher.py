"""
Placement dispatcher (ДП).

Д1ОЗ1 — put into first free slot found by ring
Д1ОО3 — if full, evict oldest then put
"""

from __future__ import annotations
from typing import Optional

from smo.model.buffer import Buffer
from smo.model.request import Request


class PlacementDispatcher:
    def __init__(self, buffer: Buffer) -> None:
        self._buffer = buffer

    def place(self, request: Request, now: float) -> Optional[Request]:
        """
        Put request into buffer.
        Returns the rejected (evicted) request, or None if no rejection.
        """
        free = self._buffer.find_free_by_ring()
        if free is not None:
            request.mark_buffered(now)
            self._buffer.put(request, free)
            return None

        # Buffer full → drop oldest (Д1ОО3)
        victim = self._buffer.evict_oldest()
        victim.mark_rejected(now)
        free2 = self._buffer.find_free_by_ring()
        assert free2 is not None
        request.mark_buffered(now)
        self._buffer.put(request, free2)
        return victim
