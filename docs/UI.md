# UI and animation contract

## Visual Direction

The application uses a modern monochrome dark theme.

The interface should feel minimal, precise, calm, and contemporary.
White cats and controls should stand out clearly against layered charcoal surfaces.

Avoid pure black across every surface. Use subtle dark-gray elevation to separate regions.

## Color Tokens

- App background: `#0D0D0F`
- Top control surface: `#161619`
- Visualizer canvas: `#111113`
- Elevated control surface: `#202024`
- Hover surface: `#29292E`
- Primary text: `#F5F5F5`
- Secondary text: `#A1A1AA`
- Muted text: `#6F6F78`
- Border: `#303036`
- Cat fill: `#F7F7F5`
- Cat secondary detail: `#D8D8D4`
- Cat shadow: `#000000` at low opacity
- Disabled content: `#55555D`

## Contrast

- Cats must remain visually dominant.
- Do not use bright accent colors in the default theme.
- Use contrast, scale, spacing, and opacity instead of decorative color.
- Avoid pure `#000000` backgrounds directly beside pure `#FFFFFF` large surfaces where possible.

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
