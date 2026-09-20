# Coditary

Central monorepo for all Coditary applications, microservices, and shared UI components.

All public projects from the [Coditary GitHub organization](https://github.com/orgs/Coditary/repositories) are included as Git submodules.

## Clone

```bash
git clone --recurse-submodules https://github.com/Coditary/Coditary.git
cd Coditary
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

Or run the setup script:

```bash
./scripts/setup-submodules.sh
```

## Structure

```
Coditary/
├── apps/                    # Standalone products and tools
├── core/                    # Shared libraries (teez, ycallr, wuji, …)
├── tools/                   # Multi-component toolchains (AST, …)
├── shared/                  # Shared C++ modules (Shared-Cpp)
├── benchmarks/              # Reproducible language & framework benchmarks
├── registry/                # Package catalogs (beez, reqpack, teez, ycallr, …)
├── templates/               # Project starters and blueprints
├── plugins/
│   ├── beez/                # Beez workflow plugins (10)
│   ├── teez/                # Optional teez runner plugins (vitest, …)
│   ├── mcps/                # MCP servers wrapping Coditary CLIs
│   ├── ycallr-apis/         # ycallr API profile definitions
│   └── reqpack/             # ReqPack registry, template, and plugins (152+)
└── tempify/                 # Tempify registry and templates (2)
```

### Apps

| Path | Repository |
|------|------------|
| `apps/axio` | [Axio](https://github.com/Coditary/Axio) |
| `apps/beez` | [Beez](https://github.com/Coditary/Beez) |
| `apps/dorch` | [Dorch](https://github.com/Coditary/Dorch) |
| `apps/dottery` | [Dottery](https://github.com/Coditary/Dottery) |
| `apps/ipmc` | [Ipmc](https://github.com/Coditary/Ipmc) |
| `apps/nexis` | [Nexis](https://github.com/Coditary/Nexis) |
| `apps/noctua` | [Noctua](https://github.com/Coditary/Noctua) |
| `apps/nxpm` | [NXPM](https://github.com/Coditary/NXPM) |
| `apps/prebyte` | [Prebyte](https://github.com/Coditary/Prebyte) |
| `apps/prebyte-2.0` | [Prebyte-2.0](https://github.com/Coditary/Prebyte-2.0) |
| `apps/parser-cli` | [parser-cli](https://github.com/Coditary/parser-cli) |
| `apps/reqpack` | [ReqPack](https://github.com/Coditary/ReqPack) |
| `apps/tempify` | [Tempify](https://github.com/Coditary/Tempify) |
| `apps/teez-cli` | [teez-cli](https://github.com/Coditary/teez-cli) |
| `apps/dappy` | [Dappy](https://github.com/Coditary/Dappy) |
| `apps/tuinator` | [Tuinator-CLI](https://github.com/Coditary/Tuinator-CLI) |
| `apps/wuji-ai` | [wuji-ai](https://github.com/Coditary/wuji-ai) |
| `apps/ycallr-cli` | [ycallr-cli](https://github.com/Coditary/ycallr-cli) |
| `apps/zshaper` | [ZShaper](https://github.com/Coditary/ZShaper) |

### Core

| Path | Repository |
|------|------------|
| `core/dappy-core` | [dappy-core](https://github.com/Coditary/dappy-core) |
| `core/parser-core` | [parser-core](https://github.com/Coditary/parser-core) |
| `core/std-cpp-parser` | [std-cpp-parser](https://github.com/Coditary/std-cpp-parser) |
| `core/teez-core` | [teez-core](https://github.com/Coditary/teez-core) |
| `core/teez-worker` | [teez-worker](https://github.com/Coditary/teez-worker) |
| `core/Tuinator` | [Tuinator](https://github.com/Coditary/Tuinator) |
| `core/wuji-core` | [wuji-core](https://github.com/Coditary/wuji-core) |
| `core/ycallr-core` | [ycallr-core](https://github.com/Coditary/ycallr-core) |

### Tools

| Path | Repository | Notes |
|------|------------|-------|
| `tools/ast` | [ast](https://github.com/Coditary/ast) | AST wire consumer toolchain (linter, formatter, refactor); producer is `core/parser-core` + `apps/parser-cli` |

### Shared

| Path | Repository |
|------|------------|
| `shared/Shared-Cpp` | [Shared-Cpp](https://github.com/Coditary/Shared-Cpp) |

### Templates

| Path | Repository |
|------|------------|
| `templates/cpp-default-project` | [CPP-Default-Project](https://github.com/Coditary/CPP-Default-Project) |
| `templates/project-blueprint` | [Project-Blueprint](https://github.com/Coditary/Project-Blueprint) |

### Plugins

- **Beez** (`plugins/beez/`): clang, conan, coverage, cppcheck, ctest, cyclonedx, fuzzer, osv-audit, pipeline, registry
- **Teez** (`plugins/teez/`): optional runner plugins (e.g. vitest); ReqPack installer at `plugins/reqpack/teez`
- **Dappy** (`plugins/dappy/`): optional adapter/target manifests (python, gdbserver, …); ReqPack installer at `plugins/reqpack/dappy`
- **ReqPack** (`plugins/reqpack/`): registry, template-wrapper, and 150+ language/tool plugins
- **MCP** (`plugins/mcps/`): Go MCP servers wrapping Coditary CLIs (reqpack, parser-cli, beez, …)
- **ycallr** (`plugins/ycallr-apis/`): API profile definitions for ycallr

### Registries

| Path | Repository |
|------|------------|
| `registry/teez` | [teez-registry](https://github.com/Coditary/teez-registry) |
| `registry/dappy` | [dappy-registry](https://github.com/Coditary/dappy-registry) |
| `registry/wuji` | [wuji-registry](https://github.com/Coditary/wuji-registry) |
| `registry/ycallr` | [ycallr-registry](https://github.com/Coditary/ycallr-registry) |

### Tempify

| Path | Repository |
|------|------------|
| `tempify/registry` | [tempify-registry](https://github.com/Coditary/tempify-registry) |
| `tempify/templates` | [tempify-templates](https://github.com/Coditary/tempify-templates) |

## Submodule count

202 public repositories are linked as submodules (203 public repos minus this monorepo itself).

Private repositories are not included.
