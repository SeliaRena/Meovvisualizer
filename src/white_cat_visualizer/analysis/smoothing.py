from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def _require_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


class AttackReleaseSmoother:
    """Vector smoother with a fast rising coefficient and slower falling coefficient."""

    def __init__(self, size: int, *, attack: float = 0.80, release: float = 0.20) -> None:
        size = _require_int(size, "size")
        if size <= 0:
            raise ValueError("size must be positive")
        for name, value in (("attack", attack), ("release", release)):
            if not np.isfinite(value) or not 0.0 < value <= 1.0:
                raise ValueError(f"{name} must be finite and in (0, 1]")
        if attack <= release:
            raise ValueError("attack must be greater than release for faster rise")

        self._attack = float(attack)
        self._release = float(release)
        self._state = np.zeros(size, dtype=np.float64)

    @property
    def state(self) -> NDArray[np.float64]:
        snapshot = self._state.copy()
        snapshot.setflags(write=False)
        return snapshot

    def reset(self, value: float = 0.0) -> None:
        if not np.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("reset value must be finite and between 0 and 1")
        self._state.fill(value)

    def process(self, target: NDArray[np.float64]) -> NDArray[np.float64]:
        values = np.asarray(target, dtype=np.float64)
        if values.shape != self._state.shape:
            raise ValueError(f"target shape must be {self._state.shape}, got {values.shape}")
        if not np.isfinite(values).all():
            raise ValueError("target must contain only finite values")
        if np.any((values < 0.0) | (values > 1.0)):
            raise ValueError("target values must be between 0 and 1")

        coefficients = np.where(values > self._state, self._attack, self._release)
        self._state += coefficients * (values - self._state)
        output = self._state.copy()
        output.setflags(write=False)
        return output
