---
name: verify-change
description: Review current changes against a phase prompt for correctness, scope, readability, performance risks, architecture, and tests. First pass is read-only.
---

# Review workflow

1. Read `AGENTS.md`, the named phase prompt, and its referenced docs.
2. Inspect `git status --short`, `git diff --stat`, `git diff --check`, and the full diff.
3. Check intended behavior before style.
4. Flag architecture drift, duplicated state, unbounded queues, hidden failures, difficult logic, speculative abstractions, and unrelated edits.
5. For audio, check formats, finite/range guarantees, callback safety, reset, and deterministic tests.
6. For QML, check per-frame allocation/JavaScript, binding loops, model replacement, resize, focus, and visual checks.
7. Run focused tests and `python scripts/verify.py`; run the benchmark for audio hot-path changes.
8. Report findings by severity with file/line references, then residual manual checks.

Do not modify code during the first review pass. If there are no material findings, say so plainly.
