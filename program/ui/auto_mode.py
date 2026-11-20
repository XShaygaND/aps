"""Automatic mode (ОР1): only the two final tables."""

from __future__ import annotations

from ui.factory import build_engine


def run_auto_mode(
    n_sources: int,
    n_devices: int,
    buffer_size: int,
    mean_ia: float,
    mean_svc: float,
    n_requests: int | None,
    seed: int = 42,
    pilot: int = 500,
) -> None:
    if n_requests is not None:
        print(f"AUTOMATIC mode  (fixed N={n_requests})")
        engine = build_engine(
            n_sources=n_sources,
            n_devices=n_devices,
            buffer_size=buffer_size,
            mean_interarrival=mean_ia,
            mean_service=mean_svc,
            max_requests=n_requests,
            seed=seed,
        )
        engine.run()
        busy = [d.busy_time for d in engine.pool.devices]
        engine.stats.print_tables(busy)
        return

    # Auto-determine N for ~10% accuracy
    print("=== Pilot run to estimate P_reject ===")
    pilot_engine = build_engine(
        n_sources=n_sources,
        n_devices=n_devices,
        buffer_size=buffer_size,
        mean_interarrival=mean_ia,
        mean_service=mean_svc,
        max_requests=pilot,
        seed=seed,
    )
    pilot_engine.run()
    p = pilot_engine.stats.overall_p_reject()
    needed = pilot_engine.stats.required_n(p=p if p > 0 else 0.05)
    print(f"Pilot P_reject ≈ {p:.4f}  →  required N ≈ {needed}")

    if needed <= pilot:
        print("Pilot already sufficient.")
        busy = [d.busy_time for d in pilot_engine.pool.devices]
        pilot_engine.stats.print_tables(busy)
        return

    print(f"\n=== Main run with N = {needed} ===")
    main_engine = build_engine(
        n_sources=n_sources,
        n_devices=n_devices,
        buffer_size=buffer_size,
        mean_interarrival=mean_ia,
        mean_service=mean_svc,
        max_requests=needed,
        seed=seed + 1,
    )
    main_engine.run()
    busy = [d.busy_time for d in main_engine.pool.devices]
    main_engine.stats.print_tables(busy)
