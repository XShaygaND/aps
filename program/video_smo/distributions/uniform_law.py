"""ИЗ2 — uniform inter-arrival / service law: U[a, b]."""

from __future__ import annotations
import random

from .random_law import RandomLaw


class UniformLaw(RandomLaw):
    def __init__(self, a: float, b: float, rng: random.Random | None = None) -> None:
        super().__init__(rng)
        if not (0 < a <= b):
            raise ValueError("UniformLaw requires 0 < a <= b")
        self._a = a
        self._b = b

    def sample(self) -> float:
        return self._rng.uniform(self._a, self._b)

    def __repr__(self) -> str:
        return f"Uniform[{self._a:.3f}, {self._b:.3f}]"
