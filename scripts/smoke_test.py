from __future__ import annotations

import math

from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode


def main() -> int:
    for mode in SyntheticMode:
        source = SyntheticAudioSource(mode, seed=42)
        analyzer = SpectrumAnalyzer()
        for _ in range(3):
            frame = analyzer.analyze(source.next_frame())
            values = (*frame.bands, frame.rms, frame.peak)
            if not all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in values):
                raise RuntimeError(f"invalid visualizer frame for {mode}")
    print("core smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
