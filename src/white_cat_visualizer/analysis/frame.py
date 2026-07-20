from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VisualizerFrame:
    bands: tuple[float, ...]
    rms: float
    peak: float

    def __post_init__(self) -> None:
        if not self.bands:
            raise ValueError("bands must not be empty")
        values = (*self.bands, self.rms, self.peak)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("visualizer values must be finite")
        if not all(0.0 <= value <= 1.0 for value in values):
            raise ValueError("visualizer values must be between 0 and 1")
