# Repository rules

## Goal

Build a small, understandable Windows desktop music visualizer with a white minimal UI and two cat visualizers. Prefer correct, measurable, boring code over clever abstractions.

## Read only what the task needs

- Always read this file and the active phase file under `prompts/`.
- Read `ARCHITECTURE.md` for layer or lifecycle changes.
- Read `docs/AUDIO.md` for audio, FFT, smoothing, threading, or WASAPI work.
- Read `docs/UI.md` for QML, layout, controls, or animation work.
- Do not read `GUIDE_zh-TW.md` unless explicitly asked; it is the human manual.

## Fixed architecture

`AudioSource -> SpectrumAnalyzer -> Runtime/Controller -> QML`

- `audio` and `analysis` must not import Qt.
- QML receives render-ready normalized values. It does not inspect PCM, run FFTs, normalize data, or own backend state.
- Python owns sources, selected source, mode, sensitivity, running/error state, bands, RMS, and peak.
- Cross-thread delivery is bounded. Prefer replacing one stale frame over growing a queue.
- Tests never require real audio hardware or wall-clock sleeps.

## Code must remain understandable

- Prefer plain modules, small classes, explicit functions, dataclasses, and Protocols.
- Keep one obvious code path. Avoid metaprogramming, service locators, dependency-injection containers, event buses, generic plugin systems, and speculative registries.
- Add an abstraction only when it removes current duplication or isolates a real boundary with at least two implementations.
- Use descriptive names and intermediate variables instead of dense expressions.
- Split long functions by responsibility, not into trivial one-line wrappers.
- Comments explain why, invariants, or performance constraints; do not narrate obvious syntax.
- Do not hide errors with broad `except Exception`, silent fallbacks, or log-and-continue behavior.
- Avoid `Any` except at an unavoidable external boundary; convert to typed project data immediately.

## Performance without obscurity

- Keep DSP vectorized with NumPy and cache stable FFT/window data.
- Do not allocate QML objects, rebuild models, or run large JavaScript loops per frame.
- Audio callbacks do the minimum work and never touch QML, disk, network, or logging.
- Optimize only measured hot paths. Keep the readable implementation unless a benchmark proves it misses the budget.
- A less readable optimization requires a benchmark, a short rationale, and tests preserving behavior.

## Scope discipline

- Implement one phase or bounded slice at a time and stop at its acceptance criteria.
- Modify only files allowed by the active phase unless a required adjacent change is explained first.
- Do not rewrite prompt, guide, or architecture files during product implementation unless the task explicitly changes a contract.
- Do not add a production dependency without explaining the need and smallest alternative.
- Every bug fix includes a regression test.
- Preserve public contracts unless the phase explicitly changes them.

## Completion gate

Run focused tests while working, then:

```bash
python scripts/verify.py
```

For audio hot paths also run:

```bash
python scripts/benchmark_analysis.py
```

Do not claim completion when required checks fail. Report the failure and stop before the next phase.
