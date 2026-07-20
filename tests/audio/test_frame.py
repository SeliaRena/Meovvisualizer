from __future__ import annotations

import numpy as np
import pytest

from white_cat_visualizer.audio.frame import AudioFrame


def test_audio_frame_owns_read_only_float32_samples() -> None:
    original = np.array([0.0, 0.5, -0.5], dtype=np.float32)
    frame = AudioFrame(original, sample_rate=48_000)
    original[1] = 1.0

    assert frame.samples.dtype == np.float32
    assert frame.samples.flags.c_contiguous
    assert not frame.samples.flags.writeable
    np.testing.assert_allclose(frame.samples, [0.0, 0.5, -0.5])


def test_audio_frame_rejects_invalid_samples() -> None:
    with pytest.raises(ValueError, match="one-dimensional"):
        AudioFrame(np.zeros((2, 2), dtype=np.float32), sample_rate=48_000)
    with pytest.raises(ValueError, match="must not be empty"):
        AudioFrame(np.array([], dtype=np.float32), sample_rate=48_000)
    with pytest.raises(ValueError, match="finite"):
        AudioFrame(np.array([np.nan], dtype=np.float32), sample_rate=48_000)
