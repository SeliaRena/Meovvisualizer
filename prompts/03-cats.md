# Phase 3 — Cat visualizers

Read: `AGENTS.md`, `ARCHITECTURE.md`, `docs/UI.md`.

## Goal

Add Long Cat Bars and Bouncing Cat Heads while preserving the Phase 2 reference bars for debugging.

## Implement

- Reusable `LongCatBar` and `BouncingCatHead` QML components.
- Mode switching among reference bars, long cats, and bouncing cats.
- Body/head/ear/squash motion mapped separately as specified in `docs/UI.md`.
- Stable baseline, canvas bounds, and adaptive spacing.
- Minimal visual/debug controls only when needed to compare deterministic modes.

## Allowed area

Presentation mode property/signals, `ui/qml/`, GUI tests, and visual demo/smoke scripts.

## Do not implement

Audio backend/runtime changes, random roaming, physics engines, shader effects, or per-frame component creation.

## Acceptance

- Silence, bass pulse, and sweep are manually checked in all three visualizer modes.
- Narrow/default/wide layouts remain readable.
- No QML binding loops, large per-frame JavaScript transforms, or whole-model replacement.
- `python scripts/verify.py` passes.

Stop after Phase 3.
