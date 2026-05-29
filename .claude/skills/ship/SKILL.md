# Skill: Ship

Pre-merge / pre-deploy checklist for the je-intervenants monorepo.

## Step 1 — Code quality

```bash
pnpm nx affected -t lint
pnpm nx affected -t typecheck
pnpm nx affected -t test
```

All must pass. Fix before continuing.

## Step 2 — Build verification

```bash
pnpm nx affected -t build
```

If a shared lib changed, this will catch any consumer that broke silently.

## Step 3 — API contract check

If both frontend and API changed in this PR:

- [ ] DTO fields in the API match what the frontend sends
- [ ] Response shape in the API matches the interface in `libs/feature/api/interfaces/`
- [ ] No new mandatory fields added to a DTO without updating frontend callers
- [ ] Route path and HTTP method unchanged (or frontend service updated)

## Step 4 — Database migrations

If any entity changed:

- [ ] A new migration file exists in `apps/je-intervenants-api/src/migrations/`
- [ ] No existing committed migration was modified
- [ ] Migration runs cleanly: `pnpm nx run je-intervenants-api:typeorm:migration:run`
- [ ] Migration is reversible (down method implemented)

## Step 5 — Environment variables

- [ ] New `environment.ts` keys are added to ALL env files: `environment.ts`, `environment.prod.ts`, `environment.staging.ts`
- [ ] New API `.env` variables are documented and added to the deployment env
- [ ] No secrets or API keys committed to source

## Step 6 — i18n

If any UI text changed or was added:

- [ ] Key exists in `assets/i18n/en.json`
- [ ] Key exists in `assets/i18n/fr.json`
- [ ] No hardcoded French or English strings in templates

## Step 7 — Manual verification

Run both servers and test the affected flows:

```bash
pnpm nx serve je-intervenants-api
pnpm nx serve je-intervenants-app    # or je-intervenants-admin
```

- [ ] Happy path works end-to-end (not just unit test level)
- [ ] Auth flow not broken (login, protected routes, 401 handling)
- [ ] No console errors or network failures in DevTools

## Step 8 — Mobile (app only, if Capacitor changed)

- [ ] `npx cap sync` was run in `apps/je-intervenants-app/`
- [ ] Native build tested on simulator or device if native code changed

## Step 9 — Commit & PR

- [ ] Commit message follows conventional commits: `feat(scope):` / `fix(scope):` / `chore(scope):`
- [ ] PR targets `staging`, not `main`
- [ ] PR description covers: what changed, how to test, env var changes if any

## Step 10 — Deploy (when ready)

```bash
# Build Docker images
pnpm nx run je-intervenants-api:docker-build
pnpm nx run je-intervenants-admin:docker-build

# Push images
pnpm nx run je-intervenants-api:docker-push
pnpm nx run je-intervenants-admin:docker-push
```

Run migrations on the target environment **before** deploying the new API image.
