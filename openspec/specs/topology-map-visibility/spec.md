### Requirement: Proper SVG Gradients
The topology map SHALL use valid SVG gradients (`<linearGradient>` or `<radialGradient>`) rather than CSS gradient functions in shape attributes.

#### Scenario: Rendering the center glow
- **WHEN** the map is rendered
- **THEN** the center anchor glow renders transparently without falling back to a solid color

### Requirement: Accessible Text Contrast
The topology map SHALL render text labels with sufficient contrast against the dynamic grid background.

#### Scenario: Viewing node labels
- **WHEN** a node label is displayed on a complex background
- **THEN** the text remains legible through adequate background padding or text shadows
