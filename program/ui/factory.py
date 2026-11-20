"""Build a ready SimulationEngine from configuration parameters."""

from __future__ import annotations
import random
from typing import Callable, Optional

from smo.laws.uniform_law import UniformLaw
from smo.laws.exponential_law import ExponentialLaw
from smo.model.source import Source
from smo.model.buffer import Buffer
from smo.model.device import Device, DevicePool
from smo.statistics.collector import StatisticsCollector
from smo.simulation.engine import SimulationEngine
from smo.events.event import Event


def build_engine(
    n_sources: int,
    n_devices: int,
    buffer_size: int,
    mean_interarrival: float,
    mean_service: float,
    max_requests: Optional[int],
    seed: int,
    on_step: Optional[Callable[[float, Event, SimulationEngine], None]] = None,
) -> SimulationEngine:
    rng = random.Random(seed)

    # ИЗ2: Uniform with mean = mean_interarrival  →  a=0.5m, b=1.5m
    a = 0.5 * mean_interarrival
    b = 1.5 * mean_interarrival
    sources = []
    for i in range(1, n_sources + 1):
        law = UniformLaw(a, b, rng=random.Random(rng.randint(0, 2**31 - 1)))
        sources.append(Source(source_id=i, interarrival_law=law))

    # ПЗ1: Exp(mu), mean = 1/mu
    mu = 1.0 / mean_service
    devices = []
    for i in range(n_devices):
        law = ExponentialLaw(mu, rng=random.Random(rng.randint(0, 2**31 - 1)))
        devices.append(Device(device_id=i, service_law=law))

    buffer = Buffer(buffer_size)
    pool = DevicePool(devices)
    stats = StatisticsCollector(n_sources)

    return SimulationEngine(
        sources=sources,
        buffer=buffer,
        pool=pool,
        stats=stats,
        max_requests=max_requests,
        on_step=on_step,
    )
