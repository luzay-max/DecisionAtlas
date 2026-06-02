## Why
The Decision Topology Map currently exhibits a severe rendering bug in light mode where the central glow renders as a solid black circle, completely obscuring the nodes and text. Additionally, text elements lack sufficient contrast.

## What Changes
- **SVG Gradient Fix**: Replace invalid CSS `radial-gradient` in the `fill` attribute with a proper SVG `<radialGradient>` definition.
- **Contrast Improvements**: Adjust text labels and anchor nodes to ensure readability across themes by using appropriate shadow or background stroke techniques.

## Capabilities

### New Capabilities
- `topology-map-visibility`: Refines the UI and rendering of the Decision Topology Map for better accessibility and correctness.

### Modified Capabilities

## Impact
- **Affected Code**: `apps/web/components/timeline/decision-topology-map.tsx`
