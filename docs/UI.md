# UI and Animation Contract

## Purpose

This document is the authoritative specification for:

- application visual direction;
- layout and responsive behavior;
- tint-glass surfaces and controls;
- long-cat and bouncing-cat visualizers;
- QML rendering constraints;
- accessibility and visual verification.

Functional behavior and architecture remain defined by the corresponding
architecture, audio, runtime, and phase specifications.

Do not duplicate this full visual specification in phase prompts.
Phase prompts should reference this document instead.

---

## Visual Direction

The application uses a minimalist transparent interface with a deep
black-purple tint-glass appearance.

The interface should feel:

- modern;
- calm;
- precise;
- lightweight;
- contemporary;
- slightly futuristic without becoming cyberpunk.

White cat visualizers are the primary visual subject.

Controls should remain visually quiet and appear integrated into the glass
surface rather than arranged as many unrelated opaque cards.

The visual language is based on:

- deep black-purple translucent surfaces;
- thin translucent white outlines;
- restrained monochrome controls;
- compact typography;
- small uppercase labels where appropriate;
- generous visual breathing room;
- very subtle violet atmospheric depth.

Do not reproduce any reference interface literally.
Use its visual language while preserving this application's existing layout,
functionality, and identity.

---

## Visual Hierarchy

The visual hierarchy must remain:

1. White cat visualizers.
2. Current audio response and motion.
3. Selected audio source and visualizer mode.
4. Sensitivity, level, start/stop, and runtime status.
5. Decorative tint-glass treatment.

Glass, borders, ambience, and shadows must never compete with the cats.

---

## Color Tokens

Centralize these values in one small QML theme or token object.

Do not scatter equivalent raw color literals throughout QML files.

### Window and glass surfaces

- Window clear: `transparent`
- Main glass: `#C20B0912`
- Main glass stronger: `#DC0D0B16`
- Secondary glass: `#991B1728`
- Elevated overlay: `#1AFFFFFF`
- Hover overlay: `#26FFFFFF`
- Pressed overlay: `#38FFFFFF`

### Borders and separators

- Strong border: `#52FFFFFF`
- Standard border: `#32FFFFFF`
- Subtle border: `#1CFFFFFF`
- Separator: `#24FFFFFF`

### Text and content

- Primary text: `#F7F7FA`
- Secondary text: `#BBB8C5`
- Muted text: `#85818E`
- Disabled text: `#5F5B68`
- Inverse text: `#111016`

### Cat colors

- Cat fill: `#FAFAFC`
- Cat secondary detail: `#D9D7DF`
- Cat outline: `#B8FFFFFF`
- Cat shadow: `#52000000`

### Accent

- Primary accent: `#A491FF`
- Soft accent: `#709E8CFF`
- Accent glow: `#358C74FF`

Accent must be used sparingly.

Acceptable uses:

- selected-source indicator;
- keyboard-focus outline;
- active mode detail;
- small level or status detail;
- subtle atmospheric tint.

Do not use accent as a large surface fill.

---

## Contrast

- Cats must remain the brightest and most visually dominant elements.
- Large pure-white surfaces are not allowed.
- Avoid using pure black across every surface.
- Use transparency, opacity, border strength, spacing, and elevation to create
  hierarchy.
- Text and controls must remain readable over both light and dark desktop
  backgrounds.
- Transparency must not reduce critical information below readable contrast.
- Error and unavailable-source states must not rely on color alone.

---

## Window and Main Surface

Where supported, the native application window should use a transparent
background.

The QML window background should remain transparent, while the application
content is carried by one dominant tinted glass surface.

The main surface should use:

- approximately 12–24 px outer inset;
- approximately 18–24 px corner radius;
- dark black-purple translucent fill;
- one thin translucent border;
- restrained low-opacity shadow;
- sufficient opacity to remain readable over a visually busy desktop.

Do not divide the application into many large floating glass cards.

Do not make important sections fully transparent.

Preserve all existing:

- resizing behavior;
- minimum size;
- window dragging;
- window controls;
- maximize and restore behavior;
- high-DPI behavior.

### Native backdrop blur

True operating-system backdrop blur is optional and platform-dependent.

If an existing safe native blur implementation is already available, it may
be reused.

Otherwise:

- preserve the tint-glass appearance using translucent QML surfaces;
- do not add a large production dependency;
- do not fake live desktop blur using screenshots;
- do not block the redesign on native backdrop blur;
- do not animate blur radius per frame.

---

## Atmospheric Background

The main surface may contain a very subtle black-purple atmospheric treatment.

Allowed:

- low-contrast violet radial tint;
- one soft blurred violet form behind the visualizer;
- faint purple light near the lower center;
- extremely slow and nearly imperceptible ambience.

Not allowed:

- bright or saturated gradients;
- neon borders;
- strong bloom;
- animated particles;
- rainbow coloring;
- rapidly moving decorative light;
- multiple full-window translucent effect layers.

Atmospheric treatment must remain quieter than the cats and controls.

---

## Layout

The application uses a resizable desktop layout.

The main content is divided vertically:

- top controls: approximately 20% of available height;
- visualizer: approximately 80% of available height.

The ratio is a design target, not a requirement to force exact dimensions
when minimum control sizes would be violated.

### Top control area

The top section contains:

- audio source selector;
- visualizer mode selector;
- sensitivity control;
- current input level;
- start/stop control;
- runtime or source error state where applicable.

On wide windows:

- controls should form a horizontally aligned toolbar;
- related controls should be visually grouped by alignment and spacing;
- use minimal separators rather than opaque containers.

On narrow windows:

- controls may wrap;
- controls may use a compact secondary row;
- labels may reduce spacing but must remain readable;
- interactive targets must remain usable.

Do not hide required controls solely to preserve the 20% ratio.

### Visualizer area

The visualizer region should:

- remain visually open;
- occupy the remaining space;
- use consistent outer margins;
- keep all cats inside its bounds;
- preserve a stable lower baseline;
- scale spacing according to band count and available width;
- avoid overlap at supported window sizes.

Do not wrap the entire visualizer in another large opaque card.

Do not place each cat in its own card.

---

## Typography

Use the existing application font unless an appropriate font is already
bundled.

Typography should feel:

- compact;
- clean;
- technical but approachable;
- highly readable.

Short control headings may use:

- uppercase;
- increased letter spacing;
- medium or semibold weight;
- secondary or muted text color.

Do not uppercase:

- audio-device names;
- error messages;
- long descriptions;
- status explanations;
- accessibility labels.

Typography must not depend on excessive font weight or glow to remain visible.

---

## Control Styling

Controls should appear embedded in the main glass surface.

Avoid opaque rectangular backgrounds behind every control.

All interactive controls must define visually distinct states for:

- normal;
- hover;
- pressed;
- selected;
- disabled;
- keyboard focus.

### Buttons

Default or unselected button:

- transparent or lightly tinted fill;
- thin translucent border;
- primary or secondary text;
- restrained hover brightening.

Selected or primary button:

- near-white fill;
- dark inverse text;
- minimal or no accent fill.

Pressed button:

- slightly stronger translucent overlay;
- subtle visual compression;
- no large bounce animation.

Disabled button:

- reduced contrast;
- no hover response;
- still readable.

### Audio source selector and combo boxes

Use:

- dark translucent field;
- compact height;
- thin translucent border;
- white primary value;
- muted supporting information;
- clear focus outline.

Popup menus must use a stronger dark-glass surface than the main field so list
items remain readable.

Selected, hovered, disabled, and unavailable items must be visually distinct.

### Visualizer mode selector

Use either:

- compact segmented controls;
- or two clearly grouped outline buttons.

The selected mode should preferably use:

- near-white fill;
- dark inverse text.

Do not use a large bright-purple selected surface.

### Sliders

Use:

- thin track;
- low-opacity inactive section;
- white or soft-violet active section;
- small circular handle;
- subtle handle enlargement on hover;
- clear keyboard-focus state.

Do not use thick saturated tracks.

### Level indicator

The level indicator should:

- remain visually subordinate to the cats;
- use white, gray, or subtle violet;
- avoid strong glow;
- expose its value accessibly;
- remain readable at silence and peak.

---

## Motion

General UI motion should feel restrained and responsive.

Recommended control-state transition duration:

- approximately 100–180 ms.

Allowed:

- opacity transitions;
- small scale changes;
- restrained surface brightening;
- smooth focus and selection transitions;
- extremely slow atmospheric ambience.

Avoid:

- springy toolbar controls;
- large panel slides;
- constant decorative animation;
- animated full-window blur;
- unnecessary animation of layout dimensions.

Audio-driven cat animation may be more expressive than surrounding UI motion.

---

## Protected Visualizer Components

The existing reusable cat visualizer components are accepted implementations
and are outside the scope of shell or theme redesign work.

Protected components include:

- long-cat delegates;
- bouncing-cat-head delegates;
- shared cat geometry;
- cat face, ears, body, and tail components;
- cat animation bindings;
- peak, transient, squash, bounce, and baseline behavior;
- visualizer model bindings and delegate lifecycle.

Unless a task explicitly requests a cat-component change, do not:

- edit these components;
- rename or move their files;
- change their public properties;
- change their geometry;
- change their colors, outlines, or shadows;
- change animation durations, easing, transforms, or data mappings;
- wrap them in new per-delegate effects;
- replace them with newly generated components;
- duplicate their implementation.

Theme and shell redesigns must adapt the surrounding interface to the existing
cat components, not adapt the cats to the new interface.

Contrast should be improved by changing:

- the window background;
- the main glass surface;
- the visualizer canvas background;
- surrounding tint and ambience;
- separators and container treatment.

If the requested visual direction cannot be completed without modifying a
protected cat component, stop and report the conflict instead of changing it.

## Long Cat Bars

Each frequency band is represented by one reusable long-cat delegate.

A long cat consists of:

- rounded stretchable body;
- small head attached at the top;
- two triangular ears;
- optional simple tail;
- minimal face details;
- subtle outline or shadow for separation from the background.

The cat should read as a rounded rectangular creature with ears rather than as
an ordinary visualizer bar with decorations attached.

### Data mapping

Map animation inputs separately:

- body height ← smoothed band value;
- head vertical offset ← band value plus transient energy;
- ear rotation ← transient energy only;
- squash and stretch ← strong peak or impulse;
- optional tail response ← low-amplitude delayed movement.

The lower baseline must remain stable.

The head should remain visually connected to the body.

The body must not become an ellipse when short.
Use a rounded-rectangle silhouette with a controlled radius.

### Motion behavior

- Attack should feel responsive.
- Release should feel smooth and slightly slower.
- Strong peaks may briefly compress and rebound.
- Ear movement must remain small.
- Avoid continuous random lateral movement.
- Silence should settle cleanly without visible jitter.

Use transforms for:

- head offset;
- ear rotation;
- squash and stretch;
- small secondary movement.

Do not rebuild the delegate when values change.

---

## Bouncing Cat Heads

Each frequency band is represented by one reusable circular or softly rounded
cat-head delegate.

A bouncing cat head consists of:

- circular or compact rounded head;
- two small ears;
- minimal facial details;
- subtle outline or shadow.

### Data mapping

- vertical offset ← smoothed band value;
- peak squash ← transient or peak;
- optional scale response ← restrained peak energy;
- optional horizontal drift ← tiny deterministic value only.

### Behavior

- All heads share a stable lower baseline at silence.
- Stronger bands move higher.
- Strong peaks may produce a short squash effect.
- Heads must not randomly roam across the canvas.
- Horizontal movement, if used, must be extremely small and deterministic.
- Silence must settle without residual drift or jitter.

Do not create physics simulation solely for this mode unless explicitly
required later.

---

## Visualizer Rendering

The visualizer canvas should remain mostly transparent.

It may use:

- subtle atmospheric tint;
- low-opacity baseline;
- muted debug information when debug mode is enabled.

It must not use:

- opaque card backgrounds for individual cats;
- bright grid lines;
- strong neon glow;
- heavy per-cat shadows;
- expensive live effects on every delegate.

White cats must remain the highest-contrast elements in both visualizer modes.

---

## QML Rules

QML is a rendering and interaction layer.

QML receives render-ready values.

QML must not:

- receive raw PCM samples;
- perform FFT calculations;
- perform frequency-band mapping;
- perform audio normalization;
- own authoritative audio or runtime state;
- create objects per audio frame;
- replace the entire model per frame;
- perform per-frame JavaScript array transforms;
- use unqualified external references;
- introduce binding loops;
- animate expensive full-window effects.

Use:

- reusable components;
- required properties;
- qualified references;
- small explicit bindings;
- transforms for head, ear, bounce, and squash animation;
- one small centralized visual-token object.

Python remains authoritative for:

- available sources;
- selected source;
- visualizer mode;
- sensitivity;
- running state;
- error state;
- band values;
- RMS;
- peak;
- source availability;
- runtime lifecycle.

Do not duplicate authoritative Python state in QML.

---

## Performance Rules

- Do not create or destroy QML objects per audio frame.
- Do not replace a complete visualizer model on each animation update.
- Avoid frame-critical JavaScript loops.
- Avoid multiple full-window transparent effect layers.
- Avoid animated blur radius.
- Avoid large live shader effects unless measured and explicitly approved.
- Preserve the current bounded runtime and frame-delivery behavior.
- Preserve stable frame rate across narrow, default, wide, and maximized
  windows.
- Visual complexity must not scale without bound with audio input.

Readability must not be sacrificed for speculative micro-optimization.

More complex optimization is acceptable only when supported by profiling or
benchmark evidence.

---

## Focus and Accessibility

All interactive controls must retain:

- keyboard navigation;
- visible keyboard-focus state;
- accessible names;
- accessible values where applicable;
- readable disabled state.

Use a thin white or soft-violet focus outline with sufficient contrast.

Error, stopped, unavailable, and selected states must not rely solely on
color.

Reduced-motion behavior must preserve usability and current state clarity.

Device names and runtime messages must remain readable and must not be
artificially uppercased.

---

## Required Visual Checks

Use deterministic synthetic input and inspect:

### Input modes

- silence;
- bass pulse;
- frequency sweep.

### Window sizes

- narrow;
- default;
- wide;
- maximized.

### Application states

- stopped;
- running;
- start and stop transition;
- source selection;
- unavailable or disconnected source where supported;
- long-cat mode;
- bouncing-cat mode;
- mode switching;
- sensitivity minimum, default, and maximum;
- low, normal, and peak level.

### Control states

- normal;
- hover;
- pressed;
- selected;
- disabled;
- keyboard focus;
- combo-box popup.

### Background readability

Where practical, inspect the transparent window over:

- light desktop content;
- dark desktop content;
- visually busy desktop content.

The main glass surface must remain readable in each case.

---

## Implementation Constraints

- Preserve the existing architecture and state ownership.
- Do not alter audio analysis as part of a visual redesign.
- Do not alter runtime threading as part of a visual redesign.
- Do not introduce a generic design-system framework.
- Do not introduce runtime theme plugins.
- Do not introduce dependency injection for visual tokens.
- Keep the theme object small and directly readable.
- Avoid scattered raw visual literals.
- Avoid JavaScript-heavy rendering logic.
- Do not add production dependencies solely for blur or decoration.
- Prefer straightforward QML over metaprogramming or dynamic component
  generation.
- Preserve existing tests, smoke checks, packaging, and accessibility behavior.