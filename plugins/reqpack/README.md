# ReqPack Plugins

This directory contains ReqPack wrapper plugins that extend the package-manager orchestrator with support for additional ecosystems.

**Full documentation:** [ReqPack Wiki](https://github.com/Coditary/ReqPack/wiki) · [Extending ReqPack](https://github.com/Coditary/ReqPack/wiki/Extending-ReqPack)

## Quick Start

The fastest way to scaffold a new ReqPack wrapper plugin is using **Tempify**:

```bash
tempify rqp-wrapper my-plugin-name \
  --set plugin_name=my-plugin-name \
  --set version=0.1.0 \
  --set summary="ReqPack wrapper for MY_PACKAGE_MANAGER" \
  --set required_binary=my-package-manager
```

> The `rqp-wrapper` template is available in [tempify-templates](https://github.com/Coditary/tempify-templates/tree/main/rqp-wrapper).

## Plugin Structure

Every ReqPack wrapper plugin follows this directory layout:

```
plugins/reqpack/<plugin-name>/
    run.lua                 # Entry point: plugin table with all API methods
    metadata.json           # Package metadata (name, version, summary, license)
    reqpack.lua             # API version and dependencies
    scripts/                # Optional helper scripts
    README.md
    API.md                  # Optional quick reference
```

## Creating a Wrapper Plugin

### 1. Scaffold with Tempify

```bash
tempify rqp-wrapper my-package-manager \
  --set plugin_name=my-package-manager \
  --set required_binary=my-pkg
```

### 2. Define the plugin entry point

Create `run.lua` with the `plugin` table:

```lua
plugin = {}

local PLUGIN_NAME = "my-package-manager"
local PLUGIN_VERSION = "0.1.0"
local REQUIRED_BINARY = "my-pkg"

local function run_exec(context, command)
    if context ~= nil and context.exec ~= nil and type(context.exec.run) == "function" then
        return context.exec.run(command)
    end
    return { success = false, stdout = "", stderr = "missing exec runner", exitCode = 127 }
end

local function build_command(arguments)
    local parts = { REQUIRED_BINARY }
    for _, arg in ipairs(arguments or {}) do
        parts[#parts + 1] = arg
    end
    return table.concat(parts, " ")
end

function plugin.getName()
    return PLUGIN_NAME
end

function plugin.getVersion()
    return PLUGIN_VERSION
end

function plugin.getRequirements()
    return {}
end

function plugin.getCategories()
    return { "Package Manager" }
end

function plugin.getSecurityMetadata()
    return {
        role = "package-manager",
        capabilities = { "exec", "network" },
        privilegeLevel = "user",
        writeScopes = {},
        networkScopes = {},
    }
end

function plugin.getMissingPackages(packages)
    -- Return packages that are not yet installed
    return packages or {}
end

function plugin.install(context, packages)
    -- Install packages
    local result = run_exec(context, build_command({ "install" }))
    return result ~= nil and result.success == true
end

function plugin.remove(context, packages)
    -- Remove packages
    return true
end

function plugin.update(context, packages)
    -- Update packages
    return true
end

function plugin.list(context)
    -- List installed packages
    return {}
end

function plugin.search(context, prompt)
    -- Search for packages
    return {}
end

function plugin.info(context, name)
    -- Get package info
    return {}
end

function plugin.outdated(context)
    -- List outdated packages
    return {}
end

function plugin.init()
    -- Check if required binary exists
    local result = run_exec(nil, "command -v " .. REQUIRED_BINARY .. " >/dev/null 2>&1")
    return result ~= nil and result.success == true
end

function plugin.shutdown()
    return true
end

return plugin
```

### 3. Define metadata

Create `metadata.json`:

```json
{
  "formatVersion": 1,
  "name": "my-package-manager",
  "version": "0.1.0",
  "summary": "ReqPack wrapper for my-package-manager",
  "description": "ReqPack Lua wrapper plugin for globally managed packages via my-package-manager CLI",
  "license": "MIT"
}
```

### 4. Define dependencies

Create `reqpack.lua`:

```lua
return {
  apiVersion = 1,
  depends = {}
}
```

## Required Plugin Methods

| Method | Description |
|--------|-------------|
| `plugin.getName()` | Returns the plugin name |
| `plugin.getVersion()` | Returns the plugin version |
| `plugin.getRequirements()` | Returns required system dependencies |
| `plugin.getCategories()` | Returns category tags for discovery |
| `plugin.getSecurityMetadata()` | Returns security capabilities and scopes |
| `plugin.getMissingPackages(packages)` | Returns packages not yet installed |
| `plugin.install(context, packages)` | Installs packages |
| `plugin.installLocal(context, path)` | Installs a local package (optional) |
| `plugin.remove(context, packages)` | Removes packages |
| `plugin.update(context, packages)` | Updates packages |
| `plugin.list(context)` | Lists installed packages |
| `plugin.search(context, prompt)` | Searches for packages |
| `plugin.info(context, name)` | Gets package information |
| `plugin.outdated(context)` | Lists outdated packages |
| `plugin.init()` | Called on plugin load; return `true` if ready |
| `plugin.shutdown()` | Called on unload |

## Context Object

The `context` parameter provides access to:

| Field | Description |
|-------|-------------|
| `context.exec.run(command)` | Execute a shell command |
| `context.tx.begin_step(label)` | Start a progress step |
| `context.tx.success()` | Mark step as successful |
| `context.tx.failed(message)` | Mark step as failed |
| `context.log.warn(message)` | Log a warning |
| `context.events[name](payload)` | Emit events |

## Testing

```bash
rqp test-plugin --plugin ./run.lua --preset core
```

## Related Wiki Pages

- [Extending ReqPack](https://github.com/Coditary/ReqPack/wiki/Extending-ReqPack) — Overview of extension models
- [Architecture](https://github.com/Coditary/ReqPack/wiki/Architecture) — System internals
- [Lua Plugin API](https://github.com/Coditary/ReqPack/wiki/Lua-Plugin-API) — Full API reference
- [Tempify Wiki](https://github.com/Coditary/Tempify/wiki) — Project template generator
- [rqp-wrapper template](https://github.com/Coditary/tempify-templates/tree/main/rqp-wrapper) — Scaffold template

## Existing Plugins

| Plugin | Description |
|--------|-------------|
| `beez` | Beez workflow plugin manager |
| `cargo` | Rust/Cargo packages |
| `conda` | Conda environments |
| `docker` | Docker images |
| `go` | Go modules |
| `gradle` | Gradle dependencies |
| `homebrew` | Homebrew packages |
| `npm` | npm global packages |
| `nuget` | NuGet packages |
| `pip` | Python pip packages |
| `pnpm` | pnpm packages |
| `yarn` | Yarn packages |
| ... | [See full list](.) |
