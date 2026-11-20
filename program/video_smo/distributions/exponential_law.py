"""ПЗ1 — exponential service law: Exp(mu), mean = 1/mu."""

from __future__ import annotations
import math
import random

from .random_law import RandomLaw


class ExponentialLaw(RandomLaw):
    def __init__(self, mu: float, rng: random.Random | None = None) -> None:
        super().__init__(rng)
        if mu <= 0:
            raise ValueError("ExponentialLaw requires mu > 0")
        self._mu = mu

    def sample(self) -> float:
        u = self._rng.random()
        while u <= 0.0:
            u = self._rng.random()
        return -math.log(u) / self._mu

    def __repr__(self) -> str:
        return f"Exp(mu={self._mu:.4f}, mean={1.0 / self._mu:.3f})"
