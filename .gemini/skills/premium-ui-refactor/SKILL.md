---
name: premium-ui-refactor
description: Audit and refactor user interfaces to apply premium UI/UX design systems. Transforms boilerplate or "cheap AI" designs into professional, custom-crafted digital experiences based on Refactoring UI and modern premium design tokens.
license: MIT
compatibility: Fully compatible with Gemini and Antigravity frameworks.
metadata:
  author: Antigravity
  version: "1.0"
---

# Premium UI Refactor Skill

This skill teaches the AI agent how to review, audit, and refactor any frontend layout, component, or style system to elevate its visual aesthetics from generic "AI-generated" boilerplate into premium, human-crafted interfaces.

## Tactical Design Rules

Apply these strict design guardrails whenever refactoring HTML, CSS, React, or Vue component layouts.

### 1. Spacing & Layout Constraints (Strict Spacing Scale)
Never use arbitrary padding or margins (e.g., `margin-top: 13px`, `padding: 27px`). Constrain all spatial relationships to a proportional geometric scale:
*   **Scale**: `2px | 4px | 8px | 12px | 16px | 24px | 32px | 48px | 64px | 96px`
*   **Alignment**: Align all elements on this grid to ensure clean vertical rhythm and structural balance.
*   **Form Inputs**: Keep interactive elements at comfortable heights (minimum `42px` touch targets).

### 2. Contrast & Typography Hierarchy (Text Weight Over Size)
Avoid increasing font sizes to create emphasis. Instead, establish depth through font weights and color contrasts:
*   **Size Constraints**: Keep type scales clean (e.g., `12px | 14px | 16px | 18px | 20px | 24px | 32px`).
*   **Weight Leverage**: Use `font-semibold` (600) or `font-medium` (500) paired with standard sizes rather than making text overly large and bold.
*   **Color Contrast**: 
    *   **Primary text**: High contrast (e.g., Slate 900 `#0f172a` in Light, Neutral 50 `#fafafa` in Dark).
    *   **Secondary text**: Slate 500 `#64748b` in Light, Neutral 400 `#a3a3a3` in Dark.
    *   **Tertiary/Muted**: Slate 400 `#94a3b8` in Light, Neutral 500 `#737373` in Dark.

### 3. Color Palette & Grayscale Foundation
Always design the skeleton and hierarchy in grayscale before injecting primary brand colors:
*   **Anti-Pattern**: Ban raw primary colors (e.g., `#FF0000` red, `#0000FF` blue). Use curated HSL palettes.
*   **Rich Dark Mode**: Do not use solid pure black (`#000000`) for backgrounds. Use deep, rich charcoal/navy grays (e.g., `#090D16` or `#0F172A`) to make borders, cards, and text pop naturally.
*   **Brand Pop**: Restrict saturated brand colors to actionable items (buttons, active status tabs, focus indicators).

### 4. Spaced & Layered Depth (Borders and Shadows)
Give components dimension. A flat 2D layout looks cheap. Use elevation and borders carefully:
*   **Card Styling**: Give cards subtle, high-quality borders rather than high-contrast dividing lines:
    *   *Light Mode*: `1px solid rgba(15, 23, 42, 0.06)` or `border-slate-100`.
    *   *Dark Mode*: `1px solid rgba(255, 255, 255, 0.08)` or `border-neutral-800`.
*   **Rounded Corners**: Avoid sharp corners. Use premium, smooth rounded corners (`rounded-xl` / `12px` or `rounded-2xl` / `16px`) for primary cards and modals.
*   **Shadows**: Use layered soft shadows. Instead of standard harsh shadows, use multiple offset shadows or diffuse ambient glows:
    *   *Ambient soft*: `box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 10px 15px -3px rgba(0, 0, 0, 0.03)`

### 5. Micro-Animations & Interactivity
Provide feedback that makes the interface feel responsive and alive:
*   **Transitions**: Ensure all hover, focus, and state transitions are smooth: `transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);`.
*   **Interactive Scales**: Add micro-interactions on hover (e.g., subtle scale-up of buttons by `1.02` or background-color shifting) to encourage interaction.

---

## Refactoring Process Flow

When the `/ui-refactor` or `/ui-polish` command is triggered on a file:

1.  **Analyze**: Look for spacing violations, contrast issues, flat 2D components, or generic colors.
2.  **Tokens Mapping**: Map current raw colors and spacings to standard scales (e.g., Tailwind tokens or HSL equivalents).
3.  **Skeleton Audit**: Strip color and review the grayscale hierarchy. Ensure the eye is guided to critical action items.
4.  **Polish Application**: Apply rounded corners, soft borders, elevation shadows, and micro-animations.
5.  **Deliver**: Output a clean, refactored version of the codebase along with an explanation of design tokens applied.
