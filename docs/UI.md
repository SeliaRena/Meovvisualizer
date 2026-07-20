# UI and animation contract

## Visual direction

A calm white desktop app, not pure white on pure white:

- app background: `#F7F7F5`
- control surface: `#FFFFFF`
- visualizer canvas: `#EDEDEA`
- primary text: `#202020`
- secondary text: `#777777`
- border: `#DDDDDA`
- cats: white with a subtle gray outline or shadow

Avoid gradients, neon, glass effects, heavy shadows, decorative clutter, and excessive rounding.

## Layout

- Resizable desktop window.
- Top controls use about 20% of height; visualizer uses about 80%.
- Controls: source, visualizer mode, sensitivity, level, start/stop.
- Wide layout is horizontal; narrow layout may wrap or use a compact row.
- Cats stay inside the canvas and share a stable lower baseline.

## Long cat bars

Each frequency band is one reusable delegate:

- rounded stretchable body
- small head on top
- two triangular ears
- optional simple tail

Map data separately:

- body height <- smoothed band value
- head offset <- band value plus transient
- ear rotation <- transient only
- squash/stretch <- strong peak

It must look like a cat reacting, not a rectangle with static ears.

## Bouncing cat heads

- one circular cat head per band
- shared baseline at silence
- vertical offset from band value
- short peak squash
- no random roaming
- any horizontal drift must be tiny and deterministic

## QML rules

- QML receives render-ready values; no PCM or FFT work.
- Use reusable components, required properties, and qualified references.
- Do not create objects or replace the whole model per frame.
- Avoid per-frame JavaScript array transforms and binding loops.
- Prefer transforms for head, ear, and squash animation.
- Python remains authoritative for source, mode, sensitivity, running/error state, bands, RMS, and peak.
- Preserve keyboard focus, visible focus state, and accessible names.

## Required visual checks

Use fixed synthetic input and inspect:

- silence
- bass pulse
- frequency sweep
- narrow, default, and wide windows
- start/stop and mode switch
