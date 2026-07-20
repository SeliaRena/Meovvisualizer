# Phase 1 — Static shell and GUI harness

Read: `AGENTS.md`, `ARCHITECTURE.md`, `docs/UI.md`.

## Goal

Create the PySide6/QML application shell with a static Python controller and a deterministic offscreen GUI smoke test.

## Implement

- `app.py` as the composition root and launch entry.
- A controller exposing static source, mode, sensitivity, running state, RMS/peak, and 24 placeholder bands.
- A resizable 2:8 white layout with the required controls and an empty/simple placeholder visualizer.
- `scripts/gui_smoke_test.py` that loads QML offscreen, checks root creation, then exits cleanly.
- Focused presentation/GUI tests where practical.

## Allowed area

`pyproject.toml`, package exports, `app.py`, `presentation/`, `ui/qml/`, GUI tests, and GUI smoke script.

## Do not implement

Audio analysis integration, real audio, worker threads, cat animation, settings persistence, or packaging.

## Acceptance

- App launches and closes without QML warnings/errors.
- Narrow/default/wide resizing does not overlap controls or leave the canvas unusable.
- Python is the only owner of application state.
- `python scripts/verify.py` passes.

Stop after Phase 1.
