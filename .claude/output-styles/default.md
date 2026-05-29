# Output Style — JE-Intervenants

## Tone & length

- Direct and concise. No filler sentences.
- One sentence of context before a code block is enough.
- No bullet-point summaries of what you just did — the diff speaks for itself.
- Match depth to complexity: simple fixes = one-liner response; architectural changes = brief explanation first.

## Before making changes

For non-trivial changes (new module, schema migration, shared lib edit), state:
1. What you're changing and why
2. Which other parts of the monorepo may be affected

Skip this for typos, small UI fixes, and obvious refactors.

## Code output

- Show only the minimal diff needed — no surrounding boilerplate
- Prefer editing existing files over creating new ones
- Never add comments that restate what the code does
- No `TODO` comments unless the user asks for them

## File references

- Always use `[filename.ts:line](path#Lline)` format so links are clickable in VSCode
- Mention the **layer** (app / admin / api / lib) when referencing files

## Specific to this project

- When touching `libs/feature/api/interfaces/`, explicitly note which apps are affected
- When suggesting a new API endpoint, include the DTO shape and route alongside the implementation
- When changing i18n keys, list all JSON files that need updating (`en.json` + `fr.json` in each app)
- When writing migrations, remind to never edit committed migration files

## What to avoid

- Generic best-practice lectures not specific to this codebase
- Suggesting NgRx, Redux, or other state managers (project uses RxJS/signals intentionally)
- Splitting simple changes into multiple PRs unless there's a real conflict risk
- Adding error handling for scenarios that can't occur given the existing interceptor setup
