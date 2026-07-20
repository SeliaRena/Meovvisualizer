# Phase 2 — Synthetic pipeline and reference bars

Read: `AGENTS.md`, `ARCHITECTURE.md`, `docs/AUDIO.md`, `docs/UI.md`.

## Goal

Replace placeholder values with the existing deterministic audio pipeline and render ordinary bars as the reference visualizer.

## Implement

- Wire `SyntheticAudioSource -> SpectrumAnalyzer -> controller -> QML`.
- Source choices for every synthetic mode and controls for sensitivity/start/stop.
- A temporary explicit QTimer-driven prototype; no worker thread yet.
- Reusable ordinary bar delegates driven by 24 render-ready values.
- RMS/peak level display and deterministic demo selection.
- Focused controller tests and an updated GUI smoke test.

## Allowed area

Existing audio/analysis code only when required, `app.py`, `presentation/`, `ui/qml/`, tests, and smoke/demo scripts.

## Do not implement

Cat shapes, Windows capture, background workers, generic plugin registries, or a second state model in QML.

## Acceptance

- Silence is visually still; bass pulse and sweep produce credible deterministic motion.
- Start/stop and source changes reset state predictably.
- No model/object recreation per frame.
- Audio benchmark shows no unexplained regression.
- `python scripts/verify.py` passes.

Stop after Phase 2.
