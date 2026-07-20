from __future__ import annotations

import argparse
import statistics
import time

from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode


def percentile(sorted_values: list[float], fraction: float) -> float:
    index = min(len(sorted_values) - 1, round((len(sorted_values) - 1) * fraction))
    return sorted_values[index]


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure deterministic spectrum analysis cost")
    parser.add_argument("--frames", type=int, default=1_000)
    parser.add_argument("--warmup", type=int, default=100)
    parser.add_argument(
        "--mode", choices=[mode.value for mode in SyntheticMode], default="seeded-noise"
    )
    args = parser.parse_args()
    if args.frames <= 0 or args.warmup < 0:
        parser.error("frames must be positive and warmup must be non-negative")

    source = SyntheticAudioSource(args.mode, seed=42)
    analyzer = SpectrumAnalyzer()
    for _ in range(args.warmup):
        analyzer.analyze(source.next_frame())

    durations_ms: list[float] = []
    for _ in range(args.frames):
        frame = source.next_frame()
        started = time.perf_counter_ns()
        analyzer.analyze(frame)
        durations_ms.append((time.perf_counter_ns() - started) / 1_000_000.0)

    durations_ms.sort()
    frame_budget_ms = source.next_frame().duration_seconds * 1_000.0
    median_ms = statistics.median(durations_ms)
    p95_ms = percentile(durations_ms, 0.95)
    worst_ms = durations_ms[-1]

    print(f"mode={args.mode} frames={args.frames}")
    print(f"analysis median={median_ms:.3f} ms p95={p95_ms:.3f} ms max={worst_ms:.3f} ms")
    print(f"source frame duration={frame_budget_ms:.3f} ms")
    print(f"p95 budget usage={p95_ms / frame_budget_ms * 100.0:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
