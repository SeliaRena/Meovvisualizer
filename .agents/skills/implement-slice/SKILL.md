---
name: implement-slice
description: Implement exactly one bounded phase or small feature in this repository, including focused tests and verification. Do not use for broad rewrites or review-only work.
---

# Bounded implementation

1. Read `AGENTS.md`, the requested phase file, and only the referenced docs.
2. Inspect affected code before editing.
3. Give a concise plan: goal, non-goals, files, tests. Do not repeat the documents.
4. Implement the smallest end-to-end behavior that meets the phase acceptance criteria.
5. Keep code explicit and readable; reject speculative abstractions and unrelated cleanup.
6. Add focused tests and run them while iterating.
7. Run `python scripts/verify.py`.
8. Inspect `git diff --check`, `git status --short`, and the final diff.
9. Stop at the phase boundary.

Report only: behavior, files changed, tests, full verification, and remaining limitations. Never claim completion after a failed required check.
