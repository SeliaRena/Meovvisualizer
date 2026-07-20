from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


def _require_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


@dataclass(frozen=True, slots=True)
class AudioFrame:
    """A validated immutable mono PCM frame."""

    samples: NDArray[np.float32]
    sample_rate: int
    frame_index: int = 0

    def __post_init__(self) -> None:
        sample_rate = _require_int(self.sample_rate, "sample_rate")
        frame_index = _require_int(self.frame_index, "frame_index")
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if frame_index < 0:
            raise ValueError("frame_index must be non-negative")

        samples = np.asarray(self.samples, dtype=np.float32)
        if samples.ndim != 1:
            raise ValueError("samples must be a one-dimensional mono array")
        if samples.size == 0:
            raise ValueError("samples must not be empty")
        if not np.isfinite(samples).all():
            raise ValueError("samples must contain only finite values")

        owned = np.ascontiguousarray(samples).copy()
        owned.setflags(write=False)
        object.__setattr__(self, "samples", owned)

    @property
    def duration_seconds(self) -> float:
        return float(self.samples.size) / self.sample_rate
