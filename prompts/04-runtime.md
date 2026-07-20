# Phase 4 — Bounded analysis runtime

Read: `AGENTS.md`, `ARCHITECTURE.md`, `docs/AUDIO.md`.

## Goal

Move source reading and spectrum analysis off the UI thread without making lifecycle logic difficult to follow.

## Implement

- A small analysis worker with explicit start, stop, and shutdown.
- A single-slot latest-frame handoff; new data replaces stale pending data.
- UI-thread delivery through narrow controller signals/properties.
- Idempotent repeated start/stop and clean application exit.
- Tests for replacement behavior, lifecycle, exceptions, and no post-stop delivery.

## Allowed area

`runtime/`, source lifecycle contract when needed, controller/composition root, focused tests, and diagnostics.

## Do not implement

Real device capture, general job schedulers, async frameworks, unbounded queues, event buses, or QML-side threading.

## Acceptance

- UI remains responsive under synthetic high-rate input.
- Queue/storage capacity is fixed and asserted by tests.
- Worker failures reach a typed controller error state.
- Shutdown does not hang or leak a running worker.
- Benchmark and `python scripts/verify.py` pass.

Stop after Phase 4.
