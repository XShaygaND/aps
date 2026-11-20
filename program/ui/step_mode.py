"""Step-by-step mode (ОД1): show sources / buffer / devices after every event."""

from __future__ import annotations

from smo.events.event import Event
from smo.simulation.engine import SimulationEngine
from ui.factory import build_engine


def _print_state(now: float, ev: Event, engine: SimulationEngine) -> None:
    print("\n" + "-" * 70)
    extra = ""
    if ev.source_id is not None:
        extra += f"  source={ev.source_id}"
    if ev.device_id is not None:
        extra += f"  device={ev.device_id}"
    print(f"t = {now:.4f}   event = {ev.type.name}{extra}")
    print("Sources:")
    for sid in sorted(engine.sources):
        print(f"  {engine.sources[sid]}")
    print(f"Buffer:  {engine.buffer}")
    print(f"Devices: {engine.pool}")
    print(f"Generated so far: {engine.stats.total_generated()}")
    input("  [Enter] next step  |  Ctrl+C to stop  ")


def run_step_mode(
    n_sources: int,
    n_devices: int,
    buffer_size: int,
    mean_ia: float,
    mean_svc: float,
    n_requests: int,
    seed: int = 42,
) -> None:
    print(f"STEP-BY-STEP mode  (N={n_requests})")
    engine = build_engine(
        n_sources=n_sources,
        n_devices=n_devices,
        buffer_size=buffer_size,
        mean_interarrival=mean_ia,
        mean_service=mean_svc,
        max_requests=n_requests,
        seed=seed,
        on_step=_print_state,
    )
    engine.run()
    busy = [d.busy_time for d in engine.pool.devices]
    engine.stats.print_tables(busy)
