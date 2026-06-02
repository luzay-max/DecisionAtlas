## Context
The topology map uses an `<svg>` to render dynamic decision nodes. The center anchor uses an invalid `fill` value that falls back to black in SVG rendering contexts.

## Goals / Non-Goals
**Goals:**
- Fix the rendering bug of the center anchor glow.
- Ensure text is readable in both light and dark themes.

**Non-Goals:**
- Complete redesign of the topology map's visual layout.

## Decisions
- **SVG `<radialGradient>`**: We will add a `<radialGradient id="center-glow">` inside the existing `<defs>` block and apply it via `fill="url(#center-glow)"`.
- **Text Readability**: We will enhance the `<text>` stroke and `<rect>` background opacity behind node labels to ensure high contrast regardless of the background theme.

## Risks / Trade-offs
- None. This is a targeted UI fix.
