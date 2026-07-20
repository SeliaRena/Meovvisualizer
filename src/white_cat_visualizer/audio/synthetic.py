from __future__ import annotations

import math
from enum import StrEnum

import numpy as np
from numpy.typing import NDArray

from white_cat_visualizer.audio.frame import AudioFrame


def _require_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


class SyntheticMode(StrEnum):
    SILENCE = "silence"
    SINE = "sine"
    BASS_PULSE = "bass-pulse"
    FREQUENCY_SWEEP = "frequency-sweep"
    IMPULSE = "impulse"
    SEEDED_NOISE = "seeded-noise"


class SyntheticAudioSource:
    """Deterministic mono PCM source used by tests and visual development."""

    def __init__(
        self,
        mode: SyntheticMode | str = SyntheticMode.SILENCE,
        *,
        sample_rate: int = 48_000,
        frame_size: int = 2_048,
        frequency_hz: float = 440.0,
        amplitude: float = 0.8,
        seed: int = 42,
    ) -> None:
        self._mode = SyntheticMode(mode)
        sample_rate = _require_int(sample_rate, "sample_rate")
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        frame_size = _require_int(frame_size, "frame_size")
        if frame_size <= 0:
            raise ValueError("frame_size must be positive")
        if not math.isfinite(frequency_hz) or frequency_hz <= 0:
            raise ValueError("frequency_hz must be finite and positive")
        if not math.isfinite(amplitude) or not 0.0 <= amplitude <= 1.0:
            raise ValueError("amplitude must be finite and between 0 and 1")
        seed = _require_int(seed, "seed")

        self._sample_rate = sample_rate
        self._frame_size = frame_size
        self._frequency_hz = frequency_hz
        self._amplitude = amplitude
        self._seed = seed
        self._frame_index = 0
        self._rng = np.random.default_rng(seed)

    @property
    def source_id(self) -> str:
        return f"synthetic:{self._mode.value}"

    @property
    def display_name(self) -> str:
        mode_name = self._mode.value.replace("-", " ").title()
        return f"Synthetic: {mode_name}"

    @property
    def mode(self) -> SyntheticMode:
        return self._mode

    def reset(self) -> None:
        self._frame_index = 0
        self._rng = np.random.default_rng(self._seed)

    def start(self) -> None:
        """Synthetic generation needs no external lifecycle work."""

    def stop(self) -> None:
        """Synthetic generation needs no external lifecycle work."""

    def next_frame(self) -> AudioFrame:
        start = self._frame_index * self._frame_size
        sample_indices = np.arange(start, start + self._frame_size, dtype=np.float64)
        time_seconds = sample_indices / self._sample_rate
        samples = self._render(sample_indices, time_seconds)
        frame = AudioFrame(
            samples=samples.astype(np.float32, copy=False),
            sample_rate=self._sample_rate,
            frame_index=self._frame_index,
        )
        self._frame_index += 1
        return frame

    def _render(
        self,
        sample_indices: NDArray[np.float64],
        time_seconds: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        match self._mode:
            case SyntheticMode.SILENCE:
                return np.zeros(self._frame_size, dtype=np.float64)
            case SyntheticMode.SINE:
                return self._amplitude * np.sin(2.0 * np.pi * self._frequency_hz * time_seconds)
            case SyntheticMode.BASS_PULSE:
                carrier = np.sin(2.0 * np.pi * 90.0 * time_seconds)
                envelope = (0.5 + 0.5 * np.sin(2.0 * np.pi * 2.0 * time_seconds)) ** 4
                return self._amplitude * carrier * envelope
            case SyntheticMode.FREQUENCY_SWEEP:
                sweep_period_seconds = 8.0
                phase_time = np.mod(time_seconds, sweep_period_seconds)
                start_hz = 50.0
                end_hz = min(12_000.0, self._sample_rate * 0.45)
                slope = (end_hz - start_hz) / sweep_period_seconds
                phase = 2.0 * np.pi * (start_hz * phase_time + 0.5 * slope * phase_time**2)
                return self._amplitude * np.sin(phase)
            case SyntheticMode.IMPULSE:
                period = max(1, self._sample_rate // 2)
                return np.where(sample_indices.astype(np.int64) % period == 0, self._amplitude, 0.0)
            case SyntheticMode.SEEDED_NOISE:
                return self._rng.uniform(
                    low=-self._amplitude,
                    high=self._amplitude,
                    size=self._frame_size,
                )
        raise AssertionError(f"unhandled synthetic mode: {self._mode}")
