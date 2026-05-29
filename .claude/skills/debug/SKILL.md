# Skill: Debug

Systematically isolate and fix issues in the monorepo across app / admin / api layers.

## Step 1 — Locate the failing layer

Ask / determine:
- Is it a **UI issue** (layout, state not rendering)? → app or admin
- Is it a **data issue** (wrong data, missing field)? → api or shared interface
- Is it a **network issue** (4xx, 5xx, no request)? → api or interceptor
- Is it a **type error** (TS compile failure)? → shared lib or DTO mismatch
- Is it a **build failure**? → run `pnpm nx affected -t build` to see which project

## Step 2 — Reproduce

```bash
# Start only what's needed
pnpm nx serve je-intervenants-api          # API on :3000
pnpm nx serve je-intervenants-app          # App web (or admin on :4300)
```

Check browser DevTools Network tab:
- Request URL and method correct?
- Request payload matches the DTO?
- Response shape matches the shared interface?

## Step 3 — Isolate by layer

### API issues

```bash
# Check API logs in terminal running nx serve
# Hit the endpoint directly
curl -H "Authorization: Bearer <token>" http://localhost:3000/v1/<route>
```

- 401 → JWT guard issue or missing `@Public()`
- 400 → DTO validation failure (check class-validator decorators)
- 500 → check NestJS error log; likely TypeORM or null ref

Common traps:
- `@Exclude()` stripping fields you need — check `ClassSerializerInterceptor`
- Migration not run — run `pnpm nx run je-intervenants-api:typeorm:migration:run`
- TypeORM relation not eager-loaded — check `relations` option in `findOne`/`find`

### Frontend issues (app / admin)

- Open DevTools → Network → find the failing request
- Check the service in `libs/feature/<domain>/` — is the response handled correctly?
- RxJS: check if the observable completes or errors silently (use `catchError`)
- Check `BaseUrlInterceptor` — relative path should start with `/v1/`
- Check `JwtInterceptor` — token present in localStorage?

Common traps:
- Missing `async` pipe in template → subscription leak or stale data
- i18n key missing in one language file → silent fallback to raw key
- Admin proxy not forwarding new route → update `proxy.conf.json`

### Shared lib issues

- Type error after interface change? Run `pnpm nx affected -t typecheck`
- Missing export? Check `libs/feature/<domain>/src/index.ts`

## Step 4 — Fix safely

- For API: if fixing requires a schema change → generate a new migration, never edit existing
- For shared interfaces: check affected projects with `pnpm nx affected -t build --dry-run`
- For frontend: write the fix in the service/lib, not in the component

## Step 5 — Verify

```bash
pnpm nx test <affected-project>
pnpm nx lint <affected-project>
```

Then manually test the golden path in browser (not just the fixed scenario).
