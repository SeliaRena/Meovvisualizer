from __future__ import annotations

import math
from itertools import pairwise

import numpy as np
from numpy.typing import NDArray

from white_cat_visualizer.analysis.frame import VisualizerFrame
from white_cat_visualizer.analysis.smoothing import AttackReleaseSmoother
from white_cat_visualizer.audio.frame import AudioFrame


def _require_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


class SpectrumAnalyzer:
    """Convert validated PCM frames into normalized logarithmic spectrum bands."""

    def __init__(
        self,
        *,
        band_count: int = 24,
        min_frequency_hz: float = 40.0,
        max_frequency_hz: float = 16_000.0,
        floor_db: float = -80.0,
        ceiling_db: float = 0.0,
        attack: float = 0.80,
        release: float = 0.20,
    ) -> None:
        band_count = _require_int(band_count, "band_count")
        if band_count <= 0:
            raise ValueError("band_count must be positive")
        if not math.isfinite(min_frequency_hz) or min_frequency_hz <= 0:
            raise ValueError("min_frequency_hz must be finite and positive")
        if not math.isfinite(max_frequency_hz) or max_frequency_hz <= min_frequency_hz:
            raise ValueError("max_frequency_hz must be greater than min_frequency_hz")
        if not math.isfinite(floor_db) or not math.isfinite(ceiling_db):
            raise ValueError("dB bounds must be finite")
        if ceiling_db <= floor_db:
            raise ValueError("ceiling_db must be greater than floor_db")

        self._band_count = band_count
        self._min_frequency_hz = float(min_frequency_hz)
        self._max_frequency_hz = float(max_frequency_hz)
        self._floor_db = float(floor_db)
        self._ceiling_db = float(ceiling_db)
        self._smoother = AttackReleaseSmoother(
            band_count,
            attack=attack,
            release=release,
        )
        self._window_cache: dict[int, NDArray[np.float64]] = {}

    @property
    def band_count(self) -> int:
        return self._band_count

    def reset(self) -> None:
        self._smoother.reset()

    def analyze(self, frame: AudioFrame) -> VisualizerFrame:
        samples = frame.samples.astype(np.float64, copy=False)
        window = self._window_for(samples.size)
        spectrum = np.abs(np.fft.rfft(samples * window))

        normalization = max(window.sum() / 2.0, np.finfo(np.float64).tiny)
        magnitude = spectrum / normalization
        frequencies = np.asarray(
            np.fft.rfftfreq(samples.size, d=1.0 / frame.sample_rate),
            dtype=np.float64,
        )
        raw_bands = self._map_bands(frequencies, magnitude, frame.sample_rate)
        smoothed = self._smoother.process(raw_bands)

        rms = float(np.sqrt(np.mean(np.square(samples))))
        peak = float(np.max(np.abs(samples)))
        return VisualizerFrame(
            bands=tuple(float(value) for value in smoothed),
            rms=float(np.clip(rms, 0.0, 1.0)),
            peak=float(np.clip(peak, 0.0, 1.0)),
        )

    def _window_for(self, size: int) -> NDArray[np.float64]:
        window = self._window_cache.get(size)
        if window is None:
            window = np.hanning(size).astype(np.float64)
            window.setflags(write=False)
            self._window_cache[size] = window
        return window

    def _map_bands(
        self,
        frequencies: NDArray[np.float64],
        magnitude: NDArray[np.float64],
        sample_rate: int,
    ) -> NDArray[np.float64]:
        nyquist = sample_rate / 2.0
        upper = min(self._max_frequency_hz, nyquist)
        if upper <= self._min_frequency_hz:
            raise ValueError(
                "sample rate is too low for the configured minimum visualized frequency"
            )

        edges = np.geomspace(self._min_frequency_hz, upper, self._band_count + 1)
        bands = np.empty(self._band_count, dtype=np.float64)
        tiny = np.finfo(np.float64).tiny

        for index, (lower, upper_edge) in enumerate(pairwise(edges)):
            if index == self._band_count - 1:
                mask = (frequencies >= lower) & (frequencies <= upper_edge)
            else:
                mask = (frequencies >= lower) & (frequencies < upper_edge)

            if np.any(mask):
                band_magnitude = float(np.max(magnitude[mask]))
            else:
                nearest = int(np.argmin(np.abs(frequencies - math.sqrt(lower * upper_edge))))
                band_magnitude = float(magnitude[nearest])

            band_db = 20.0 * math.log10(max(band_magnitude, tiny))
            bands[index] = np.clip(
                (band_db - self._floor_db) / (self._ceiling_db - self._floor_db),
                0.0,
                1.0,
            )

        return bands
