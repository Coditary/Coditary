#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CLI="$ROOT/apps/ycallr-cli"
CORE="$ROOT/core/ycallr-core"
LINK="$ROOT/apps/ycallr-core"
if [[ ! -e "$LINK" ]]; then
  echo "missing apps/ycallr-core -> core/ycallr-core symlink" >&2
  exit 1
fi
cd "$CLI"
exec cargo run --quiet --manifest-path Cargo.toml -- import-openapi "$@"
