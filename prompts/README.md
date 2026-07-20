# Phase order

Run one phase per Codex implementation thread. Codex reads the file from disk; do not paste all project documents into chat.

| Phase | File | Main skill |
|---|---|---|
| 1 | `01-shell.md` | `$implement-slice` |
| 2 | `02-bars.md` | `$implement-slice $audio-pipeline` |
| 3 | `03-cats.md` | `$implement-slice` |
| 4 | `04-runtime.md` | `$implement-slice $audio-pipeline` |
| 5 | `05-windows-audio.md` | `$implement-slice $audio-pipeline` |
| 6 | `06-release.md` | `$implement-slice` |

Implementation request:

```text
Use the named skills. Implement prompts/0N-....md exactly. Read only the files it references. Stop after this phase.
```

Review in a separate thread:

```text
Use $verify-change. Review Phase N against prompts/0N-....md. Do not modify files.
```
