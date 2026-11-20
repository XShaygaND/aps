"""Statistics for ОР1 tables + required-N formula."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import math

from smo.model.request import Request


@dataclass
class SourceStats:
    generated: int = 0
    rejected: int = 0
    completed: int = 0
    sum_wait: float = 0.0
    sum_wait_sq: float = 0.0
    sum_service: float = 0.0
    sum_service_sq: float = 0.0
    sum_sojourn: float = 0.0
    sum_sojourn_sq: float = 0.0

    def on_generated(self) -> None:
        self.generated += 1

    def on_rejected(self) -> None:
        self.rejected += 1

    def on_completed(self, req: Request) -> None:
        self.completed += 1
        w = req.wait_time or 0.0
        s = req.service_time or 0.0
        t = req.sojourn_time or 0.0
        self.sum_wait += w
        self.sum_wait_sq += w * w
        self.sum_service += s
        self.sum_service_sq += s * s
        self.sum_sojourn += t
        self.sum_sojourn_sq += t * t

    @property
    def p_reject(self) -> float:
        return self.rejected / self.generated if self.generated else 0.0

    def mean_wait(self) -> float:
        return self.sum_wait / self.completed if self.completed else 0.0

    def mean_service(self) -> float:
        return self.sum_service / self.completed if self.completed else 0.0

    def mean_sojourn(self) -> float:
        return self.sum_sojourn / self.completed if self.completed else 0.0

    def var_wait(self) -> float:
        n = self.completed
        if n < 2:
            return 0.0
        m = self.mean_wait()
        return (self.sum_wait_sq - n * m * m) / (n - 1)

    def var_service(self) -> float:
        n = self.completed
        if n < 2:
            return 0.0
        m = self.mean_service()
        return (self.sum_service_sq - n * m * m) / (n - 1)


class StatisticsCollector:
    def __init__(self, n_sources: int) -> None:
        self.sources: Dict[int, SourceStats] = {
            i: SourceStats() for i in range(1, n_sources + 1)
        }
        self.total_time: float = 0.0

    def record_generated(self, req: Request) -> None:
        self.sources[req.source_id].on_generated()

    def record_rejected(self, req: Request) -> None:
        self.sources[req.source_id].on_rejected()

    def record_completed(self, req: Request) -> None:
        self.sources[req.source_id].on_completed(req)

    def set_total_time(self, t: float) -> None:
        self.total_time = t

    def total_generated(self) -> int:
        return sum(s.generated for s in self.sources.values())

    def overall_p_reject(self) -> float:
        g = self.total_generated()
        if g == 0:
            return 0.0
        r = sum(s.rejected for s in self.sources.values())
        return r / g

    def required_n(
        self,
        p: float | None = None,
        delta: float = 0.1,
        t_alpha: float = 1.643,
    ) -> int:
        """N = t²(1-p)/(p·δ²) for ~10% relative accuracy, conf ≈ 0.9."""
        if p is None:
            p = self.overall_p_reject()
        if p <= 0.0:
            return 5000
        n = (t_alpha ** 2) * (1 - p) / (p * delta ** 2)
        return max(100, int(math.ceil(n)))

    def print_tables(self, devices_busy: List[float]) -> None:
        print("\n" + "=" * 78)
        print("TABLE 1 — Source characteristics")
        print("=" * 78)
        print(
            f"{'Src':>4} {'Gen':>7} {'Rej':>6} {'P_otk':>8} "
            f"{'T_wait':>10} {'T_serv':>10} {'T_soj':>10} "
            f"{'Var_w':>10} {'Var_s':>10}"
        )
        print("-" * 78)
        for sid in sorted(self.sources):
            s = self.sources[sid]
            print(
                f"{sid:>4} {s.generated:>7} {s.rejected:>6} {s.p_reject:>8.4f} "
                f"{s.mean_wait():>10.4f} {s.mean_service():>10.4f} "
                f"{s.mean_sojourn():>10.4f} "
                f"{s.var_wait():>10.4f} {s.var_service():>10.4f}"
            )
        print("=" * 78)

        print("\nTABLE 2 — Device utilization")
        print("=" * 40)
        print(f"{'Dev':>4} {'Busy time':>12} {'K_isp':>10}")
        print("-" * 40)
        T = self.total_time if self.total_time > 0 else 1.0
        for i, busy in enumerate(devices_busy):
            print(f"{i:>4} {busy:>12.4f} {busy / T:>10.4f}")
        print("=" * 40)
        print(f"Simulation horizon T = {T:.4f}")
        print(f"Overall P_reject   = {self.overall_p_reject():.4f}")
        print(f"Total generated    = {self.total_generated()}")
