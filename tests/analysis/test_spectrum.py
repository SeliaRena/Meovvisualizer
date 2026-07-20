from __future__ import annotations

import math

import numpy as np
import pytest

from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode


def analyzer_without_smoothing() -> SpectrumAnalyzer:
    return SpectrumAnalyzer(attack=1.0, release=0.999)


def test_silence_produces_near_zero_bands() -> None:
    frame = SyntheticAudioSource(SyntheticMode.SILENCE).next_frame()
    result = analyzer_without_smoothing().analyze(frame)
    assert max(result.bands) <= 1e-12
    assert result.rms == 0.0
    assert result.peak == 0.0


def test_low_sine_activates_lower_region() -> None:
    frame = SyntheticAudioSource(SyntheticMode.SINE, frequency_hz=120.0).next_frame()
    result = analyzer_without_smoothing().analyze(frame)
    dominant = int(np.argmax(result.bands))
    assert dominant < len(result.bands) // 2


def test_high_sine_activates_upper_region() -> None:
    frame = SyntheticAudioSource(SyntheticMode.SINE, frequency_hz=8_000.0).next_frame()
    result = analyzer_without_smoothing().analyze(frame)
    dominant = int(np.argmax(result.bands))
    assert dominant >= len(result.bands) // 2


@pytest.mark.parametrize("mode", list(SyntheticMode))
def test_all_output_values_are_finite_and_normalized(mode: SyntheticMode) -> None:
    source = SyntheticAudioSource(mode)
    analyzer = SpectrumAnalyzer()
    result = analyzer.analyze(source.next_frame())
    values = (*result.bands, result.rms, result.peak)

    assert all(math.isfinite(value) for value in values)
    assert all(0.0 <= value <= 1.0 for value in values)
