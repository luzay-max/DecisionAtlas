## Why

The current Landing Page (`page.tsx`) uses a functional MVP layout that does not reflect the premium aesthetic standards of the project. To deliver a world-class SaaS entry point, we need a massive UI/UX overhaul using Crystal Aurora / Obsidian Dark aesthetics, Bento grids, and fluid motion as outlined by our `ui-ux-pro-max-skill` guidelines. This will dramatically improve user engagement and perceived product quality.

## What Changes

- **Hero Section Overhaul**: Replace basic text elements with a massive, animated "Crystal Aurora / Obsidian Dark" background gradient and upgraded typography.
- **Bento Grid Refactor**: Replace standard `<ol>` / `<ul>` lists for steps and concepts with a responsive Bento Grid layout.
- **Glassmorphism Panels**: Apply heavy frosted glass effects (`backdrop-blur-xl`, semi-transparent background, 1px subtle borders) to the `GuidedDemoPanel` and advanced controls.
- **Interaction & Motion**: Introduce stagger-sequence entrance animations for grid items and subtle scale effects on interactive elements, adhering to minimum touch target constraints.

## Capabilities

### New Capabilities
- `landing-page-aesthetic`: Comprehensive aesthetic overhaul for the landing page incorporating Bento Grid layouts, Glassmorphism, and Fluid Motion.

### Modified Capabilities
- (None)

## Impact

- **Affected Code**: `apps/web/app/page.tsx`, `apps/web/components/guided-demo/guided-demo-panel.tsx`, and `apps/web/app/globals.css`.
- **UI/UX**: Vastly improved first impression for users landing on the application.
- **Performance**: Animations and CSS changes must be tested to ensure no Cumulative Layout Shift (CLS) or performance regressions.
