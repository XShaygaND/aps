"""
Discrete-event simulation engine (principle of special states).

Variant 16: ИБ ИЗ2 ПЗ1 Д1ОЗ1 Д1ОО3 Д2П2 Д2Б2
"""

from __future__ import annotations
from typing import Callable, Dict, List, Optional

from smo.model.source import Source
from smo.model.buffer import Buffer
from smo.model.device import DevicePool
from smo.events.event import Event
from smo.events.event_type import EventType
from smo.events.event_calendar import EventCalendar
from smo.dispatchers.placement_dispatcher import PlacementDispatcher
from smo.dispatchers.selection_dispatcher import SelectionDispatcher
from smo.statistics.collector import StatisticsCollector


class SimulationEngine:
    def __init__(
        self,
        sources: List[Source],
        buffer: Buffer,
        pool: DevicePool,
        stats: StatisticsCollector,
        max_requests: Optional[int] = None,
        horizon: float = 1e12,
        on_step: Optional[Callable[[float, Event, "SimulationEngine"], None]] = None,
    ) -> None:
        self.sources: Dict[int, Source] = {s.id: s for s in sources}
        self.buffer = buffer
        self.pool = pool
        self.stats = stats
        self.max_requests = max_requests
        self.horizon = horizon
        self.on_step = on_step  # callback for step-by-step UI

        self.now: float = 0.0
        self.calendar = EventCalendar()
        self.placement = PlacementDispatcher(buffer)
        self.selection = SelectionDispatcher(buffer, pool, self.calendar)

        for s in sources:
            t = s.schedule_next(0.0)
            self.calendar.add(EventType.ARRIVAL, t, source_id=s.id)

    # ------------------------------------------------------------------ handlers
    def _handle_arrival(self, ev: Event) -> None:
        src = self.sources[ev.source_id]  # type: ignore[index]
        req = src.generate(self.now)
        self.stats.record_generated(req)

        next_t = src.schedule_next(self.now)
        if next_t <= self.horizon:
            if self.max_requests is None or self.stats.total_generated() < self.max_requests:
                self.calendar.add(EventType.ARRIVAL, next_t, source_id=src.id)

        victim = self.placement.place(req, self.now)
        if victim is not None:
            self.stats.record_rejected(victim)

        self.selection.dispatch(self.now)

    def _handle_completion(self, ev: Event) -> None:
        req = self.pool.finish(ev.device_id, self.now)  # type: ignore[arg-type]
        self.stats.record_completed(req)
        self.selection.dispatch(self.now)

    # ------------------------------------------------------------------ main loop
    def run(self) -> None:
        while True:
            if (
                self.max_requests is not None
                and self.stats.total_generated() >= self.max_requests
                and self.buffer.is_empty()
                and self.pool.all_free()
            ):
                break

            ev = self.calendar.next()
            if ev is None:
                break

            # ignore future arrivals once we reached the request limit
            if (
                self.max_requests is not None
                and self.stats.total_generated() >= self.max_requests
                and ev.type == EventType.ARRIVAL
            ):
                continue

            self.now = ev.time

            if ev.type == EventType.ARRIVAL:
                self._handle_arrival(ev)
            else:
                self._handle_completion(ev)

            if self.on_step is not None:
                self.on_step(self.now, ev, self)

        self.stats.set_total_time(self.now)
