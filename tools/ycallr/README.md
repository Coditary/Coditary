# ycallr — Pling development (monorepo layout)

| Path | Role |
|------|------|
| `apps/ycallr-cli` | CLI (submodule) |
| `apps/ycallr-core` | Symlink → `core/ycallr-core` (for local `cargo` path deps) |
| `core/ycallr-core` | Engine (submodule) |
| `plugins/ycallr-apis` | Official YAML profiles (`a/`–`z/`) |
| `registry/ycallr` | ReqPack catalog |

Scripts in `scripts/` assume the Coditary repo root is three levels above `scripts/`.

```bash
./tools/ycallr/scripts/import-openapi.sh spec.yaml --name my-api --out plugins/ycallr-apis/m/my-api.yaml
```

See `AGENTS.md` and `PROFILE_STYLE.md` in this directory.
