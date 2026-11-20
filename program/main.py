#!/usr/bin/env python3
"""
Variant 16 — Operational video-stream analysis simulator

Formula: ИБ  ИЗ2  ПЗ1  Д1ОЗ1  Д1ОО3  Д2П2  Д2Б2  ОР1  ОД1

Usage:
  python main.py                  # automatic, auto-N
  python main.py --step           # step-by-step
  python main.py --requests 3000  # automatic, fixed N
"""

from __future__ import annotations
import argparse
import sys

from ui.step_mode import run_step_mode
from ui.auto_mode import run_auto_mode


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Variant 16 — Video-stream analysis SMO"
    )
    parser.add_argument("--step", action="store_true",
                        help="Step-by-step mode")
    parser.add_argument("--requests", type=int, default=None,
                        help="Fixed number of requests")
    parser.add_argument("--pilot", type=int, default=500,
                        help="Pilot size for auto-N")
    parser.add_argument("--sources", type=int, default=3)
    parser.add_argument("--devices", type=int, default=2)
    parser.add_argument("--buffer", type=int, default=5)
    parser.add_argument("--arrival-mean", type=float, default=5.0)
    parser.add_argument("--service-mean", type=float, default=4.0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("Variant 16  |  ИБ ИЗ2 ПЗ1 Д1ОЗ1 Д1ОО3 Д2П2 Д2Б2 ОР1 ОД1")
    print(
        f"sources={args.sources}  devices={args.devices}  "
        f"buffer={args.buffer}  mean_IA={args.arrival_mean}  "
        f"mean_SVC={args.service_mean}\n"
    )

    if args.step:
        n = args.requests or 30
        run_step_mode(
            args.sources, args.devices, args.buffer,
            args.arrival_mean, args.service_mean, n, args.seed,
        )
    else:
        run_auto_mode(
            args.sources, args.devices, args.buffer,
            args.arrival_mean, args.service_mean,
            args.requests, args.seed, args.pilot,
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)
