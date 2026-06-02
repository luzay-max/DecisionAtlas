## 1. CSS & Token Preparation

- [x] 1.1 Add Bento Grid utility classes and Glassmorphism variables to `apps/web/app/globals.css`
- [x] 1.2 Add `@keyframes` for `enterFromBottom` and `shimmer` animations in `globals.css`

## 2. Core Components Refactor

- [x] 2.1 Update `GuidedDemoPanel` in `apps/web/components/guided-demo/guided-demo-panel.tsx` to use heavy frosted glass (`backdrop-blur-xl`, border, semi-transparent bg) and shimmer on the primary CTA
- [x] 2.2 Refactor `AdvancedControls` in `apps/web/components/guided-demo/advanced-controls.tsx` (if needed) to align with the new glassmorphism aesthetics

## 3. Landing Page (page.tsx) Overhaul

- [x] 3.1 Refactor Hero Section in `page.tsx`: replace standard text with an animated gradient background and semantic typography for `h1`
- [x] 3.2 Refactor the layout of Concepts and Steps in `page.tsx` from `ul`/`ol` lists to a responsive Bento Grid layout (`grid`, `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`)
- [x] 3.3 Apply entrance animations to the Bento Grid items and `transform: scale(0.98)` on press for all action links
- [x] 3.4 Ensure all touch targets on mobile satisfy the >= 44x44px minimum requirement

## 4. Verification

- [x] 4.1 Run Lighthouse / Axe accessibility check and ensure text contrast >= 4.5:1
- [x] 4.2 Verify layout on mobile viewport (e.g., 375px) using responsive mode or E2E scripts
