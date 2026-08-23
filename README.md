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
├── apps/                    # Standalone products and tools (14)
├── benchmarks/              # Reproducible language & framework benchmarks
├── templates/               # Project starters and blueprints
├── plugins/
│   ├── beez/                # Beez workflow plugins (10)
│   └── reqpack/             # ReqPack registry, template, and plugins (152)
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
| `apps/reqpack` | [ReqPack](https://github.com/Coditary/ReqPack) |
| `apps/tempify` | [Tempify](https://github.com/Coditary/Tempify) |
| `apps/wuji-ai` | [wuji-ai](https://github.com/Coditary/wuji-ai) |
| `apps/zshaper` | [ZShaper](https://github.com/Coditary/ZShaper) |

### Templates

| Path | Repository |
|------|------------|
| `templates/cpp-default-project` | [CPP-Default-Project](https://github.com/Coditary/CPP-Default-Project) |
| `templates/project-blueprint` | [Project-Blueprint](https://github.com/Coditary/Project-Blueprint) |

### Plugins

- **Beez** (`plugins/beez/`): clang, conan, coverage, cppcheck, ctest, cyclonedx, fuzzer, osv-audit, pipeline, registry
- **ReqPack** (`plugins/reqpack/`): registry, template-wrapper, and 150 language/tool plugins under `plugins/`

### Tempify

| Path | Repository |
|------|------------|
| `tempify/registry` | [tempify-registry](https://github.com/Coditary/tempify-registry) |
| `tempify/templates` | [tempify-templates](https://github.com/Coditary/tempify-templates) |

## Submodule count

181 public repositories are linked as submodules (182 public repos minus this monorepo itself).

Private repositories are not included.
