# Architecture

## Data flow

```text
AudioSource
  -> immutable mono float32 AudioFrame
SpectrumAnalyzer
  -> immutable normalized VisualizerFrame
Analysis runtime / VisualizerController
  -> Qt properties and narrow signals
QML
  -> layout and visual transforms only
```

Dependencies point in one direction. Lower layers never import higher layers.

## Target layout

```text
src/white_cat_visualizer/
  audio/
    frame.py
    source.py
    synthetic.py
    windows_loopback.py       # Phase 5
  analysis/
    frame.py
    smoothing.py
    spectrum.py
  runtime/                    # Phase 4
    latest_frame.py
    analysis_worker.py
  presentation/               # Phase 1+
    visualizer_controller.py
    source_model.py
  ui/qml/                     # Phase 1+
    Main.qml
    components/
    visualizers/
  app.py                      # composition root
```

The composition root creates concrete objects directly. Do not add a dependency-injection framework.

## Contracts

### AudioFrame

- one-dimensional mono samples
- contiguous `float32`
- finite and non-empty
- positive sample rate
- immutable to consumers

### VisualizerFrame

- fixed band count for a running analyzer
- bands, RMS, and peak are finite in `[0.0, 1.0]`
- immutable to consumers

### AudioSource

Synthetic and Windows sources expose the same small lifecycle contract. Backend-specific formats are converted at the backend boundary.

## State ownership

Python owns all application and audio state. QML owns only temporary presentation animation derived from Python values, such as a brief ear rotation or squash transform.

Use narrow properties/signals. Do not emit a global change signal for every frame when only bands, RMS, and peak changed.

## Runtime model

Before Phase 4, synthetic analysis may be driven by a QTimer as a temporary, explicit prototype.

From Phase 4 onward:

1. The source publishes PCM without touching QML.
2. The worker analyzes only the newest pending frame.
3. A single-slot latest-frame handoff replaces stale data.
4. The controller transfers the newest normalized frame to the UI thread.
5. Stop and shutdown are explicit, idempotent, and tested.

Low latency is more important than processing every historical frame.

## Windows scope

Phase 5 captures the selected Windows output endpoint using WASAPI loopback. This is system-mix capture for that device, not per-application capture. Per-process audio is outside the MVP.
