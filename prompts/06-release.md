# Phase 6 — Optional release hardening

Read: `AGENTS.md`, `ARCHITECTURE.md`, `docs/UI.md`; read `docs/AUDIO.md` only for measured audio changes.

## Goal

Make the verified MVP comfortable to use and distributable without adding product scope.

## Implement only justified items

- Persist source, mode, sensitivity, and window settings.
- Keyboard navigation, focus visuals, and accessible names.
- Debug overlay for FPS, processing time, dropped/replaced frames; off by default.
- Profile and fix measured frame-time or allocation problems.
- Application metadata, icon hooks, and a documented Windows build command.
- Final README usage and known limitations.

## Allowed area

Existing layers, settings adapter, diagnostics, packaging metadata/scripts, tests, and README.

## Do not implement

New visualizer types, themes, cloud features, recording, per-app capture, plugin frameworks, or broad rewrites.

## Acceptance

- Core and GUI verification pass from a clean environment.
- Settings failures have safe explicit fallback behavior.
- No debug logs/overlay enabled by default.
- Release build starts on Windows and synthetic fallback remains available.
- Known limitations are honest and specific.

Stop after Phase 6.
