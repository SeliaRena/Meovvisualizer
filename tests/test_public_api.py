from __future__ import annotations

import white_cat_visualizer as package


def test_public_api_is_importable() -> None:
    assert package.AudioFrame is not None
    assert package.SpectrumAnalyzer is not None
    assert package.SyntheticAudioSource is not None
