# Skill: Code Review

Perform a structured review of the current branch changes. Focus on what matters for this monorepo specifically.

## Steps

### 1. Get the diff

```bash
git diff staging...HEAD --stat
git diff staging...HEAD
```

### 2. Identify the scope

For each changed file, determine which layer it belongs to:
- `apps/je-intervenants-app/` → **app**
- `apps/je-intervenants-admin/` → **admin**
- `apps/je-intervenants-api/` → **api**
- `libs/` → **shared lib** (flag: affects all consumers)

### 3. Review checklist

#### Shared libs (`libs/`)
- [ ] Did the interface change break existing consumers? Run `pnpm nx affected -t build --dry-run`
- [ ] Are new enums prefixed with `E`?
- [ ] Are new interfaces exported from the lib's `index.ts`?
- [ ] No business logic in `libs/feature/api/interfaces/` — types only

#### API (`apps/je-intervenants-api/`)
- [ ] New routes have JWT guard or explicit `@Public()` decorator
- [ ] DTOs use `class-validator` decorators — no unvalidated inputs
- [ ] Sensitive fields have `@Exclude()` on the entity
- [ ] New entity fields have a corresponding migration (not in existing committed migration)
- [ ] TypeORM relations use correct cascade settings
- [ ] Pagination uses `nestjs-paginate` — no manual `skip`/`take`
- [ ] New interfaces added to `libs/feature/api/interfaces/` for frontend consumers

#### Frontend — app & admin
- [ ] HTTP calls are in feature lib services, not in components
- [ ] Errors are forwarded to `ToastsService`, not swallowed
- [ ] New UI strings are in `assets/i18n/en.json` AND `fr.json` — no hardcoded strings
- [ ] New feature modules are lazy-loaded via routing
- [ ] Smart/dumb split respected: no HTTP calls in `ui/` components
- [ ] No inline `environment.apiUrl` URL construction — use relative paths + `BaseUrlInterceptor`

#### App-specific
- [ ] After new Capacitor plugin: `npx cap sync` mentioned in PR description
- [ ] No hardcoded platform checks unless behind Capacitor `isPlatform()`

#### Admin-specific
- [ ] Proxy conf updated if new API path pattern is added

### 4. API contract alignment

When a PR touches both frontend and API:
- [ ] DTO fields match what the frontend sends
- [ ] Response shape matches the shared interface in `libs/feature/api/interfaces/`
- [ ] HTTP method and route path are consistent across API controller + frontend service

### 5. Output format

Report grouped by layer. For each issue:
- File + line link
- What's wrong
- Suggested fix (one line)

End with a **verdict**: Approve / Request changes / Needs discussion.
