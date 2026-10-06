# Dispatch: Explorer Survey R2 (Frontend Architecture & React Bits)

## Working Directory
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_r2_1`

## Authoritative Reference
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md`

## Objectives
1. Investigate R2 (Frontend Architecture):
   - Inspect `web/src/components/ui/`: list all files and custom UI primitives present.
   - Inspect all Next.js pages and components in `web/src/app/`, `web/src/components/`: check where custom primitives or `shadcn/ui` or related packages (e.g. `@radix-ui/*`, `class-variance-authority`, `clsx`, etc.) are imported.
   - Investigate React Bits (https://reactbits.dev/): how React Bits components are structured (React Bits is a copy-paste component library for React/Tailwind/Framer Motion, providing animated backgrounds, text animations, components, etc.).
   - Check `web/package.json`: verify dependencies. Identify if any `shadcn` or competing UI libraries are installed or referenced.
   - Plan how to rip out conflicting custom primitives from `web/src/components/ui/` and refactor pages to use React Bits components cleanly while keeping tests (`pnpm run test`, `pnpm exec playwright test`) working.
2. Produce a structured handoff report in `handoff.md` with concrete evidence, file paths, line numbers, and recommended surgical remediation steps.

## 2026-10-06T03:31:43Z
You are an Explorer subagent for the Resume & Job Matching Talent Marketplace Engine project.
Your identity: teamwork_preview_explorer_survey_r2_1
Your working directory: c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_r2_1

MANDATORY FIRST STEP: Read the authoritative user request at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md
Also read your assignment at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_r2_1\DISPATCH.md

Your Task:
Investigate Requirement R2 (Frontend Architecture & React Bits):
1. Inspect `web/src/components/ui/`: catalog all custom UI primitives currently present.
2. Inspect Next.js pages and components in `web/src/app/` and `web/src/components/`: find every usage/import of custom UI primitives, `shadcn/ui`, and related libraries.
3. Check `web/package.json`: check all dependencies and devDependencies. Verify if `shadcn` or competing libraries exist.
4. Investigate React Bits (https://reactbits.dev/): understand how React Bits components are structured (animated components, backgrounds, cards, etc. typically using Framer Motion and Tailwind).
5. Plan the refactoring to:
   - Rip out conflicting custom UI primitives in `web/src/components/ui/`
   - Refactor Next.js pages to exclusively use React Bits components for UI, backgrounds, and animations.
   - Ensure `shadcn/ui` or competing libraries are eliminated.
   - Ensure `pnpm run test` (vitest) and `pnpm exec playwright test` continue to pass or are appropriately updated to match the React Bits components.

Output:
Write a comprehensive, structured technical report to:
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_r2_1\handoff.md`
and notify me via send_message when complete.
