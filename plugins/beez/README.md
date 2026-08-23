# Beez Plugins

This directory contains Beez plugins that extend the build and task orchestrator with additional functionality.

**Full documentation:** [Beez Wiki](https://github.com/Coditary/Beez/wiki) · [Plugin System](https://github.com/Coditary/Beez/wiki/Plugin-System)

## Quick Start

The fastest way to scaffold a new Beez plugin is using **Tempify**:

```bash
tempify beez_plugin my-plugin-name \
  --set plugin_name=my-plugin-name \
  --set organization=myorg \
  --set version=1.0.0 \
  --set description="My custom plugin"
```

> A Beez plugin template for Tempify is coming soon. Check the [Tempify Wiki](https://github.com/Coditary/Tempify/wiki) for updates.

## Plugin Structure

Every Beez plugin follows this directory layout:

```
plugins/beez/<plugin-name>/
    beez_plugin.lua      # Entry point: plugin(), steps, config
    beez.package.json    # Package metadata
    src/                 # Lua modules (runner, config, defaults, ...)
    LICENSE
    README.md
```

## Creating a Plugin

### 1. Define the plugin entry point

Create `beez_plugin.lua` with the `plugin()` declaration:

```lua
local defaults = require("src.defaults")

plugin("my-plugin", {
    version = "1.0.0",
    description = "Description of what your plugin does",
    organization = "myorg",

    config = {
        defaults = {
            binary = defaults.binary,
            -- more default values...
        },

        profile_defs = {
            default = {
                -- profile-specific overrides
            },
        },

        finalize = function(resolved)
            -- post-process resolved config
            return resolved
        end,
    },

    steps = {
        my_step = {
            phase = "quality",       -- standard phase
            scope = "analyze",       -- standard scope
            input = defaults.patterns,
            description = "What this step does",
            config = { profile = "default" },
            run = function(ctx)
                return require("src.runner").run(ctx)
            end,
        },
    },
})
```

### 2. Implement your modules

Create the `src/` directory with your Lua modules:

| File | Purpose |
|------|---------|
| `defaults.lua` | Default configuration values, file patterns |
| `config.lua` | Config normalization and validation |
| `runner.lua` | Step execution logic (receives `ctx`) |
| `command.lua` | Command building helpers |
| `output.lua` | Output parsing and formatting |
| `cache.lua` | Cache key generation (optional) |

### 3. Load the plugin in your project

In your project's `build.lua`:

```lua
reqpack {
    beez = {
        {
            name = "myorg/my-plugin",
            path = "./plugins/beez/my-plugin",
            version = "1.0.0",
        },
    },
}
```

For local development, point `path` directly to your plugin directory.

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Phase** | When a step runs (e.g., `setup`, `quality`, `compile`, `verify`) |
| **Scope** | What a step targets (e.g., `app`, `analyze`, `security`) |
| **Step** | A single unit of work with a `run` callback |
| **Config DSL** | Plugin configuration with `defaults`, `profile_defs`, `finalize` |
| **`ctx`** | Step context providing access to config, filesystem, and workers |

## Related Wiki Pages

- [Plugin System](https://github.com/Coditary/Beez/wiki/Plugin-System) — Full plugin API reference
- [Lua DSL](https://github.com/Coditary/Beez/wiki/Lua-DSL) — `build.lua` reference
- [Phases and Scopes](https://github.com/Coditary/Beez/wiki/Phases-and-Scopes) — Standard phase/scope names
- [Caching](https://github.com/Coditary/Beez/wiki/Caching) — How step caching works
- [Lua API](https://github.com/Coditary/Beez/wiki/Lua-API-Overview) — `beez.fs`, `beez.net`, `beez.data`, etc.
- [Tempify Wiki](https://github.com/Coditary/Tempify/wiki) — Project template generator

## Existing Plugins

| Plugin | Description |
|--------|-------------|
| `clang` | Clang tooling (format, tidy, etc.) |
| `conan` | Conan package manager integration |
| `coverage` | Code coverage analysis |
| `cppcheck` | Incremental cppcheck static analysis |
| `ctest` | CTest integration |
| `cyclonedx` | CycloneDX SBOM generation |
| `fuzzer` | Fuzz testing support |
| `osv-audit` | OSV vulnerability auditing |
| `pipeline` | Pipeline orchestration utilities |
