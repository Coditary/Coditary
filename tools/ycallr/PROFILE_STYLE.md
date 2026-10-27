# ycallr API Profile Style Guide

Unified conventions for all Plings in `ycallr-apis/`. Every agent-generated profile **must** follow this document so CLI output feels consistent across APIs.

## File layout

```
ycallr-apis/
  <first-letter>/<name>.yaml    # e.g. g/github.yaml, s/sentry.yaml
  openapi-specs/<name>/         # downloaded OpenAPI sources (optional, gitignored if large)
```

## Top-level profile

| Field | Rule |
|-------|------|
| `name` | Lowercase slug, matches filename without `.yaml` (e.g. `github`, `sentry`) |
| `version` | `"1.0.0"` until API vendor version is tracked separately |
| `description` | One English sentence: what API + primary use case |
| `base_url` | Production default; no trailing slash |

## Environment & auth

- One primary secret env var per profile, `required: true`, UPPER_SNAKE_CASE.
- Never embed secrets in YAML; use `${ENV_VAR}` only.
- Name auth block after purpose (`token`, `api`, `bearer`) — use the same name in every command's `auth:` field.

Standard env names:

| API | Env var(s) |
|-----|---------|
| GitHub | `GITHUB_TOKEN` |
| GitLab | `GITLAB_TOKEN` |
| Grafana | `GRAFANA_TOKEN` (edit `base_url` in profile) |
| Sentry | `SENTRY_AUTH_TOKEN` |
| Cloudflare | `CLOUDFLARE_API_TOKEN` |
| CircleCI | `CIRCLECI_TOKEN` |
| Datadog | `DD_API_KEY`, `DD_APP_KEY` |
| DigitalOcean | `DIGITALOCEAN_TOKEN` |
| PagerDuty | `PAGERDUTY_API_KEY` |
| Docker Hub | `DOCKERHUB_TOKEN` |
| Bitbucket | `BITBUCKET_USERNAME`, `BITBUCKET_APP_PASSWORD` |
| Buildkite | `BUILDKITE_API_TOKEN` |
| Jira | `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN` (edit `base_url`) |
| Slack | `SLACK_BOT_TOKEN` |
| Supabase | `SUPABASE_ACCESS_TOKEN` |
| Terraform Cloud | `TF_API_TOKEN` |
| Netlify | `NETLIFY_AUTH_TOKEN` |
| Fly.io | `FLY_API_TOKEN` |
| Render | `RENDER_API_KEY` |
| Railway | `RAILWAY_TOKEN` |
| Hetzner | `HETZNER_TOKEN` |
| Vercel | `VERCEL_TOKEN` |

## Command tree

1. **Nest by domain**, not flat operationIds: `repos → issues → list`, not `repos-issues-list`.
2. **Leaf names**: verb-first, lowercase, kebab-case: `list`, `get`, `create`, `update`, `delete`, `resolve`.
3. **Group nodes** (no HTTP call): always have `description:`; no `endpoint`/`method`.
4. **Leaf nodes**: always have `description`, `endpoint`, `method`, `params`, `responses`.
5. Prefer **space-separated CLI paths** that read like English: `ycallr github repos issues list`.

Import hints:

- GitHub: `--preset github --nest-by tag --short-names`
- Others: `--preset none --nest-by tag --short-names` (or `path` when tags are weak)

## Parameters

- Every param: `description`, `type`, `required`.
- Use `enum` when the API documents fixed values.
- Path params in `{braces}` in endpoint; still document in `params` when not implicit.

## User-facing messages (English)

All `responses.*.message` and `errors.*` strings are **for humans**, not logs. Write complete sentences.

### Success messages

Pattern: **what happened + useful fields from `{output.*}` or `{input.*}`**.

```yaml
# Good
message: "Created issue #{output.number}: {output.title}"
message: "Found {output.total_count} open issue(s) in {input.owner}/{input.repo}"
message: "Rate limit: {output.rate.remaining} remaining, resets at {output.rate.reset}"

# Bad
message: "Success"
message: "OK"
message: "{output}"
```

Use `{input.field}` for values the user passed; `{output.field}` for API response body.

### API-level `errors` block

Always define at profile root:

```yaml
errors:
  default: "<Service> API error {status}: {output.message}"
  401: "Authentication failed — check <ENV_VAR> is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the resource may not exist or you cannot access it"
  422: "Invalid request — {output.message}"
  429: "Rate limited — retry after the window shown in response headers"
```

Customize per API when the vendor documents specific error shapes (GitHub, Sentry, etc.).

### Per-command `responses`

| Key | Use |
|-----|-----|
| `success` | 200/201/204 with friendly summary |
| `"201"` / `"204"` | When message differs from generic success |
| `failure` | Optional; only if more specific than root `errors` |

Avoid generic `"Error occurred"`. If the API returns `{output.message}`, `{output.errors}`, or `{output.error}`, reference them.

## Headers

- Put shared headers on commands that need them (GitHub: `Accept`, `X-GitHub-Api-Version`).
- Content-Type on POST/PUT/PATCH with JSON bodies.

## Scope and coverage

When the vendor publishes a usable OpenAPI 3 spec, import the **full** spec (not a curated subset):

```bash
scripts/import-openapi.sh <openapi-file> --name <name> --out ycallr-apis/<letter>/<name>.yaml \
  --nest-by tag --short-names
scripts/patch-profile-auth.py   # normalize env/auth/errors after bulk import
ycallr install ycallr-apis/<letter>/<name>.yaml
```

For APIs without a full OpenAPI 3 spec (Slack, Docker Hub, Vercel) or tiny public registries (npm, crates.io), write a hand profile covering the endpoints you need.

After import, polish only the **top-level** header (`env`, `auth`, `errors`) — bulk imports keep auto-generated per-command messages.

## Validation checklist

```bash
/home/Leodoras/.local/bin/ycallr install ycallr-apis/<letter>/<name>.yaml
/home/Leodoras/.local/bin/ycallr <name> --tree
```

Fix YAML until install succeeds. Document the profile in `ycallr-apis/README.md` table.

## Import tooling

```bash
/home/Leodoras/Dev/Coditary/tools/ycallr/scripts/import-openapi.sh \
  <openapi-file> --name <name> --out ycallr-apis/<letter>/<name>.yaml [options]
```

After import: **always** manually polish auth, env, errors, and every success message per this guide.
