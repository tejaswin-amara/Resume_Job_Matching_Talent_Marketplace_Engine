# Dispatch: Worker M2 (Frontend Architecture & React Bits Refactoring)

## Working Directory
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation_m2_1`

## Authoritative Reference
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md`

## Explorer Investigation Report
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_r2_1\handoff.md`

## Scope & File Ownership
You exclusively own and modify all files under `web/`:
- `web/src/components/ui/` (to be removed completely)
- `web/src/components/reactbits/` (new React Bits component suite)
- `web/src/app/page.tsx`
- `web/src/app/candidates/page.tsx`
- `web/src/app/recruiter/page.tsx`
- `web/src/app/recruiter/allocate/page.tsx`
- `web/src/components/score-breakdown.tsx`
- `web/tests/components/Badge.test.tsx`

## Objectives
1. **Rip out custom UI primitives in `web/src/components/ui/`**:
   - Delete `badge.tsx`, `button.tsx`, `card.tsx`, `progress-bar.tsx` from `web/src/components/ui/`.
   - Remove directory `web/src/components/ui/`. Ensure no `shadcn/ui` imports exist anywhere in the frontend.
2. **Build React Bits component suite in `web/src/components/reactbits/`**:
   - Implement the React Bits components as detailed in `teamwork_preview_explorer_survey_r2_1/handoff.md`:
     - `SpotlightCard.tsx` (Card container with mouse tracking glow)
     - `Squares.tsx` (Interactive canvas/grid background)
     - `StarBorder.tsx` (Rotating border gradient action button)
     - `ShinyText.tsx` (Continuous animated gleaming gradient text)
     - `CountUp.tsx` (Smooth animated number display for scores/metrics)
     - `AnimatedBadge.tsx` (Translucent glass status badge with neon glow)
     - `AnimatedProgress.tsx` (Animated progress bar with glowing fill)
     - `index.ts` (Clean barrel export)
3. **Refactor Next.js pages to exclusively use React Bits**:
   - `web/src/app/page.tsx`: use `SpotlightCard`, `ShinyText`, `Squares`.
   - `web/src/app/candidates/page.tsx`: use `SpotlightCard`, `AnimatedBadge`, `StarBorder`.
   - `web/src/app/recruiter/page.tsx`: use `SpotlightCard`, `AnimatedBadge`, `StarBorder`, `CountUp`.
   - `web/src/app/recruiter/allocate/page.tsx`: use `SpotlightCard`, `AnimatedBadge`, `StarBorder`.
   - `web/src/components/score-breakdown.tsx`: use `AnimatedProgress`.
4. **Update Vitest component test**:
   - Update `web/tests/components/Badge.test.tsx` to test `AnimatedBadge` from `@/components/reactbits/AnimatedBadge` (or barrel export), asserting rendering and variants.
5. **Verify execution**:
   - Run `pnpm --prefix web run test` (Vitest) and verify all component tests pass.
   - Run `pnpm --prefix web exec playwright test` and verify passing.
   - Run `pnpm --prefix web run build` (Next.js build) and verify 0 errors.

## Verification Required
- Document exact commands and output in `handoff.md`.


## 2026-10-06T03:43:44Z
You are a Worker subagent for the Resume & Job Matching Talent Marketplace Engine project.
Your identity: worker_remediation_m2_1
Your working directory: c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation_m2_1

Scope & File Ownership:
You exclusively own and modify files in `web/`:
- `web/src/components/ui/` (remove completely)
- `web/src/components/reactbits/` (new React Bits component suite)
- `web/src/app/page.tsx`
- `web/src/app/candidates/page.tsx`
- `web/src/app/recruiter/page.tsx`
- `web/src/app/recruiter/allocate/page.tsx`
- `web/src/components/score-breakdown.tsx`
- `web/tests/components/Badge.test.tsx`

Implement all requirements for M2:
1. Delete custom mock primitives in `web/src/components/ui/` and remove `web/src/components/ui/`.
2. Build genuine React Bits components in `web/src/components/reactbits/` (`SpotlightCard`, `Squares`, `StarBorder`, `ShinyText`, `CountUp`, `AnimatedBadge`, `AnimatedProgress`, `index.ts`).
3. Refactor Next.js pages to exclusively import and use React Bits components.
4. Align `web/tests/components/Badge.test.tsx` to test the React Bits `AnimatedBadge`.
5. Run tests:
   - `pnpm --prefix web run test` (Vitest)
   - `pnpm --prefix web exec playwright test`
   - `pnpm --prefix web run build` (Next.js build)
Verify that all pass cleanly.
