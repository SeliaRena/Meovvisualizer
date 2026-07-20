from __future__ import annotations

import numpy as np
import pytest

from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode


@pytest.mark.parametrize("mode", list(SyntheticMode))
def test_synthetic_source_is_deterministic_after_reset(mode: SyntheticMode) -> None:
    source = SyntheticAudioSource(mode, seed=123)
    first = source.next_frame().samples.copy()
    second = source.next_frame().samples.copy()

    source.reset()

    assert np.array_equal(source.next_frame().samples, first)
    assert np.array_equal(source.next_frame().samples, second)


def test_silence_is_zero() -> None:
    source = SyntheticAudioSource(SyntheticMode.SILENCE)
    assert np.count_nonzero(source.next_frame().samples) == 0


def test_invalid_synthetic_configuration_fails_clearly() -> None:
    with pytest.raises(ValueError, match="frame_size"):
        SyntheticAudioSource(frame_size=0)
    with pytest.raises(ValueError, match="amplitude"):
        SyntheticAudioSource(amplitude=1.1)
