"""Abstract base for random inter-arrival / service laws."""

from __future__ import annotations
from abc import ABC, abstractmethod
import random


class RandomLaw(ABC):
    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    @abstractmethod
    def sample(self) -> float:
        """Return next positive interval."""
        ...
