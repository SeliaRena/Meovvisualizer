from __future__ import annotations

import argparse
import time

from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode

_BLOCKS = " ▁▂▃▄▅▆▇█"


def render(values: tuple[float, ...]) -> str:
    return "".join(
        _BLOCKS[min(len(_BLOCKS) - 1, round(value * (len(_BLOCKS) - 1)))] for value in values
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic console spectrum demo")
    parser.add_argument(
        "--mode", choices=[mode.value for mode in SyntheticMode], default="bass-pulse"
    )
    parser.add_argument("--frames", type=int, default=80)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--delay", type=float, default=0.04)
    args = parser.parse_args()

    source = SyntheticAudioSource(args.mode, seed=args.seed)
    analyzer = SpectrumAnalyzer()
    for _ in range(args.frames):
        result = analyzer.analyze(source.next_frame())
        print(
            f"\r{render(result.bands)}  rms={result.rms:0.3f} peak={result.peak:0.3f}",
            end="",
            flush=True,
        )
        if args.delay > 0:
            time.sleep(args.delay)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
