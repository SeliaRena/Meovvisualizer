# Phase 5 — Windows output loopback and source control

Read: `AGENTS.md`, `ARCHITECTURE.md`, `docs/AUDIO.md`, `docs/UI.md`.

## Goal

Add selected-output-device WASAPI loopback behind the existing source contract and make source failures understandable in the UI.

## Implement

- Enumerate Windows output endpoints with stable IDs and display names.
- Capture the selected endpoint's system mix through WASAPI loopback.
- Convert backend channel/sample format once to mono contiguous `float32`.
- Integrate source selection, start/stop, disconnect/error state, and recovery.
- Keep all synthetic sources available for tests and visual debugging.
- Mock/fake backend tests for conversion, lifecycle, removal, and errors.

## Allowed area

Windows backend, source model/controller, composition root, minimal UI error/source controls, tests, and dependency metadata.

## Do not implement

Per-application capture, microphone capture, audio routing/mixing, recording, network audio, or backend-specific logic in QML.

## Acceptance

- Unsupported platforms fail clearly without breaking core imports/tests.
- Device removal does not freeze the UI or silently stop.
- Repeated source changes and start/stop are safe.
- Callback rules and fixed-capacity handoff remain intact.
- `python scripts/verify.py` passes; manual Windows loopback check is documented.

Stop after Phase 5.
