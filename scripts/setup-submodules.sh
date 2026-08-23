#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

add_submodule() {
  local path="$1"
  local repo="$2"

  if [[ -d "$path/.git" || -f "$path/.git" ]]; then
    echo "skip (exists): $path"
    return 0
  fi

  mkdir -p "$(dirname "$path")"
  echo "add: $path <- $repo"
  git submodule add --force "https://github.com/Coditary/${repo}.git" "$path"
}

# Core applications and tools
add_submodule "apps/axio" "Axio"
add_submodule "apps/beez" "Beez"
add_submodule "apps/dorch" "Dorch"
add_submodule "apps/dottery" "Dottery"
add_submodule "apps/ipmc" "Ipmc"
add_submodule "apps/nexis" "Nexis"
add_submodule "apps/noctua" "Noctua"
add_submodule "apps/nxpm" "NXPM"
add_submodule "apps/prebyte" "Prebyte"
add_submodule "apps/prebyte-2.0" "Prebyte-2.0"
add_submodule "apps/reqpack" "ReqPack"
add_submodule "apps/tempify" "Tempify"
add_submodule "apps/wuji-ai" "wuji-ai"
add_submodule "apps/zshaper" "ZShaper"

# Benchmarks (may already exist at repo root)
add_submodule "benchmarks" "Benchmarks"

# Project templates
add_submodule "templates/cpp-default-project" "CPP-Default-Project"
add_submodule "templates/project-blueprint" "Project-Blueprint"

# Beez plugins
for repo in beez-clang beez-conan beez-coverage beez-cppcheck beez-ctest beez-cyclonedx beez-fuzzer beez-osv-audit beez-pipeline beez-registry; do
  name="${repo#beez-}"
  add_submodule "plugins/beez/${name}" "$repo"
done

# ReqPack ecosystem
add_submodule "plugins/reqpack/registry" "rqp-registry"
add_submodule "plugins/reqpack/template-wrapper" "reqpack-plugin-template-wrapper"

while IFS= read -r repo; do
  name="${repo#rqp-plugin-}"
  add_submodule "plugins/reqpack/plugins/${name}" "$repo"
done < <(gh repo list Coditary --limit 500 --json name,isPrivate --jq '.[] | select(.isPrivate == false) | select(.name | startswith("rqp-plugin-")) | .name' | sort)

# Tempify ecosystem
add_submodule "tempify/registry" "tempify-registry"
add_submodule "tempify/templates" "tempify-templates"

echo "Done. Submodule count: $(git submodule status | wc -l)"
