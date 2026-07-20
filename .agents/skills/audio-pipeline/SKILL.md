---
name: audio-pipeline
description: Implement or review PCM sources, FFT bands, smoothing, audio runtime, or Windows WASAPI loopback in this project. Do not use for QML-only styling.
---

# Audio workflow

Read `docs/AUDIO.md`, `ARCHITECTURE.md`, and affected code.

Preserve these invariants:

- Pure audio/analysis code has no Qt dependency.
- Backend input becomes mono contiguous finite `float32` at one boundary.
- Tests use deterministic synthetic frames, not hardware or sleeps.
- Analyzer output is immutable, finite, and normalized to `[0, 1]`.
- Use a Hann window, real FFT, documented log bands, and attack/release unless a tested change is justified.
- Cross-thread storage is fixed-capacity and stale frames may be replaced.
- Callbacks never block, log per frame, run FFT, touch QML, or access disk/network.
- The first Windows backend is output-endpoint loopback, not per-app capture.

Prefer NumPy vectorization and cached stable buffers over clever Python loops. After a hot-path change run focused audio/analysis tests, `python scripts/benchmark_analysis.py`, and `python scripts/verify.py`.
