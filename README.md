# White Cat Visualizer — Compact Codex Starter

A small Python 3.11 + PySide6/QML starter for a white cat music visualizer. It includes a tested deterministic audio core, three focused Codex skills, six phase prompts, and one verification command.

## Setup on Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,gui]"
python scripts/verify.py
```

Install the Windows loopback dependency only for Phase 5:

```powershell
python -m pip install -e ".[dev,gui,windows-audio]"
```

## Existing harness

```powershell
python scripts/verify.py
python scripts/visual_demo.py --mode bass-pulse
python scripts/benchmark_analysis.py
```

The current core provides deterministic PCM sources, FFT/log-band analysis, attack/release smoothing, normalized immutable frames, tests, smoke checks, and a benchmark. GUI and Windows capture are intentionally added phase by phase.

## Codex workflow

From the repository root:

```text
Use $implement-slice. Implement prompts/01-shell.md exactly. Read only the files it references. Stop after this phase.
```

Then use a separate review thread:

```text
Use $verify-change. Review Phase 1 against prompts/01-shell.md. Do not modify files.
```

Continue in the order listed in `prompts/README.md`. The complete Traditional Chinese operating guide is `GUIDE_zh-TW.md`; Codex is instructed not to read it during normal implementation.
