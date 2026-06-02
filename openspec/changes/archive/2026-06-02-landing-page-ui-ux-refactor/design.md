## Context

The current `apps/web/app/page.tsx` serves as a functional MVP landing page. However, it lacks the polish required for a top-tier SaaS product. We recently introduced the `ui-ux-pro-max-skill`, which outlines strict aesthetic rules for a "Crystal Aurora" light theme and "Obsidian" dark theme, utilizing Glassmorphism, Bento grids, and high-quality interaction patterns. We need to refactor the landing page to implement these rules.

## Goals / Non-Goals

**Goals:**
- Completely overhaul `page.tsx` using a premium Bento Grid layout.
- Implement Glassmorphism and semantic typography rules.
- Add fluid CSS/Framer Motion entrance animations.

**Non-Goals:**
- Redesigning the internal dashboard or authentication flows in this specific PR (limited to landing page).
- Rewriting backend APIs.

## Decisions

- **Bento Grid Layout**: We will use CSS Grid (`display: grid`, `grid-template-areas` or span utilities) to construct a responsive Bento grid for the product concepts and steps.
- **Glassmorphism Panels**: We will use Tailwind's `backdrop-blur-xl`, `bg-white/10`, and `border-white/20` (adapted for themes) to create the frosted glass effect on the `GuidedDemoPanel` and advanced controls.
- **Animation Strategy**: We will use pure CSS keyframes (`@keyframes`) for entrance animations (staggered via `animation-delay`) to keep the bundle size small, avoiding the overhead of heavy animation libraries unless complex gesture tracking is needed.

## Risks / Trade-offs

- **Risk: Performance Impact of Blurs** -> Mitigation: Use `backdrop-blur` sparingly (only on major panels like `GuidedDemoPanel`) and ensure `will-change: transform` is used if needed.
- **Risk: Mobile Responsiveness** -> Mitigation: The Bento Grid will collapse into a single column (`grid-cols-1`) on mobile breakpoints (`max-w-md`), ensuring a seamless mobile-first experience.
