# AGENTS.md — ycallr Pling-Entwicklung

Anleitung für AI-Agents und Contributors, die neue **Plings** (API-Profile) für [ycallr](https://github.com/Coditary/ycallr-cli) schreiben.

**Kernidee:** ycallr ruft HTTP-APIs über **deklarative YAML-Profile** auf. Statt für jede API eigene CLI-Skripte, Auth-Logik und Response-Parsing zu pflegen, beschreibt man Endpoints, Parameter, Auth und Ausgabe-Templates in YAML. ycallr-core kompiliert das Profil zu Protobuf (`.pb`), die CLI führt Befehle über die C-FFI aus.

Offizielle Referenz:

- [ycallr-cli Wiki](https://github.com/Coditary/ycallr-cli/wiki)
- [ycallr-core Wiki — API Profiles](https://github.com/Coditary/ycallr-core/wiki/API-Profiles)

---

## Was ist ein Pling?

Ein **Pling** ist ein installierbares **API-Profil**: eine YAML-Datei, die eine Remote-API beschreibt (`base_url`, Auth, Env-Vars, verschachtelte Commands). Nach `ycallr install` liegt eine kompilierte `.pb`-Datei im Config-Verzeichnis; alle Aufrufe laufen darüber.

```
ycallr-cli  →  ycallr-core (FFI)  →  HTTP-Client  →  Remote API
       ↑
  YAML-Profil (.yaml → .pb)
```

| Repo | Rolle |
|------|-------|
| [ycallr-core](https://github.com/Coditary/ycallr-core) | Engine: YAML-Parsing, Validierung, Protobuf-Kompilierung, Call-Engine, HTTP, C-FFI, WASM |
| [ycallr-cli](https://github.com/Coditary/ycallr-cli) | Dünne CLI: Argument-Parsing, Prompts, Output-Formatierung — **kein** direkter `YcallrClient`-Zugriff |
| `plugins/ycallr-apis/` (dieses Workspace) | Offizielle YAML-Profile (`a/`–`z/` nach erstem Buchstaben des API-Namens) |
| `registry/ycallr/` (Monorepo) | ReqPack-Katalog für CLI- und API-Pakete |

**Wichtig:** Neue Plings brauchen **keinen Rust-Code**. Nur YAML (+ optional Registry-Eintrag). Engine-Änderungen gehören nach `ycallr-core`, CLI-UX nach `ycallr-cli`.

---

## Architektur auf einen Blick

### ycallr-core (Engine)

| Komponente | Aufgabe |
|------------|---------|
| YAML-Parser | Strikte Ingest-Validierung beim Install |
| Protobuf-Compiler | YAML → `.pb` via `proto/api.proto` |
| Call-Engine | Templates, Env-Auflösung, Auth, Body, Response-Messages |
| HTTP-Client | `reqwest`, SSRF-sicher (keine Redirects, Host-Validierung) |
| C-FFI | C-ABI (`ycallr.h`) für CLI und andere Sprachen |
| OpenAPI-Import | OpenAPI 3.x → YAML (Feature `openapi`) |

### ycallr-cli (Frontend)

| Datei | Aufgabe |
|-------|---------|
| `src/main.rs` | CLI-Einstieg |
| `src/ffi_api.rs` | Safe Wrapper um `ycallr.h` |
| `packaging/reqpack/` | ReqPack `.rqp`-Templates |
| `scripts/ci/` | Release tar/zip und ReqPack-Packaging |

### Install-Pfade

```
~/.config/ycallr/apis/<name>.yaml   # Quelle (optional, user-managed)
~/.config/ycallr/apis/<name>.pb     # kompiliert (von ycallr install)
```

Override: `YCALLR_CONFIG_DIR`

---

## YAML-Profil: Top-Level-Felder

| Feld | Beschreibung |
|------|--------------|
| `name` | Profilname — wird CLI-Subcommand und Dateiname der `.pb` |
| `version` | Versionsstring |
| `description` | Kurzbeschreibung |
| `base_url` | API-Root-URL |
| `env` | Deklarierte Umgebungsvariablen für `${VAR}`-Templates |
| `auth` | Named Auth-Configs (Bearer, API-Key, Basic, Custom Header) |
| `errors` | Optionale API-weite Fehler-Templates (HTTP-Status → Message) |
| `commands` | Baum verschachtelter Commands |

### Minimales Beispiel

```yaml
name: my-api
version: "1.0.0"
description: Example REST API
base_url: https://api.example.com

env:
  - name: MY_API_TOKEN
    required: true

auth:
  token:
    type: bearer
    token: ${MY_API_TOKEN}

errors:
  default: "API error {status}: {output.message}"
  401: "Authentication failed — check MY_API_TOKEN"

commands:
  health:
    description: Health check
    endpoint: /health
    method: GET
    auth: token
    params: {}
    responses:
      success:
        message: "API is {output.status}"
```

Referenz in core: `ycallr-core/examples/github_api.yaml` (Beispiel, nicht Teil dieses Repos)

---

## Commands: Baum, Endpoints, Hybrid-Nodes

Commands sind **verschachtelt**. Die Engine löst Pfade per Dot-Notation auf, z. B. `repos.issues.create`.

### Leaf-Command (HTTP-Aufruf)

```yaml
commands:
  repos:
    description: Repositories
    commands:
      get:
        description: Get a repository
        endpoint: /repos/{owner}/{repo}
        method: GET
        auth: token
        headers:
          Accept: application/json
        params:
          owner:
            description: Repository owner
            type: string
            required: true
          repo:
            description: Repository name
            type: string
            required: true
        responses:
          success:
            message: "Repository {output.full_name}"
```

### Hybrid-Commands

Ein Knoten kann **gleichzeitig** einen eigenen Endpoint haben **und** Kind-Commands (z. B. `repos` als GET `/repos` und als Parent von `issues`). Siehe [API Profiles Wiki](https://github.com/Coditary/ycallr-core/wiki/API-Profiles).

### Path-Parameter

- Endpoints nutzen `{param}`-Platzhalter.
- Path-Platzhalter funktionieren **ohne** `params:`-Eintrag (implizit required).
- Query/Body-Parameter brauchen explizite `params:`-Definition.

### Param-Typen

| Typ | YAML |
|-----|------|
| String | `type: string` |
| Zahl | `type: number` |
| Boolean | `type: boolean` |
| Enum | `type: string` + `enum: [open, closed]` |

---

## Auth, Secrets, Env

Secrets **nie** im YAML hardcoden — nur `${ENV_VAR}`:

```yaml
env:
  - name: MY_API_TOKEN
    required: true

auth:
  token:
    type: bearer
    token: ${MY_API_TOKEN}
```

- Auflösung zur Laufzeit aus der Shell (`EnvMode::Auto`).
- Die kompilierte `.pb` enthält **keinen** Token-Wert.
- Unterstützte Auth-Typen: Bearer, API-Key (header/query/cookie), HTTP Basic, Custom Header.
- Cookie-Auth lehnt Injection-Zeichen ab (`;`, CRLF).

Pro Command: `auth: <name>` verweist auf einen Eintrag unter `auth:`.

---

## Body

Pro Command **genau ein** Body-Typ: JSON, Form, Multipart oder Raw.

```yaml
create:
  endpoint: /items
  method: POST
  headers:
    Content-Type: application/json
  params:
    title: { type: string, required: true }
    body: { type: string, required: false }
  # implizites JSON-Body aus params (wenn vom Profil so definiert)
```

Runtime-Override: `body` in `call()` überschreibt die YAML-Body-Definition (FFI/API-Nutzung).

---

## Responses und Fehler-Templates

Templated Messages nutzen `{input.*}` und `{output.*}`:

```yaml
responses:
  success:
    message: "Found {output.total_count} item(s)"
  "201":
    message: "Created #{output.number}: {output.title}"
```

- Fehlende Felder bleiben als Platzhalter (`{output.missing}`), werden nicht leer.
- Fallback-Reihenfolge: command-level `responses` → API-root `errors` → `{status}` in Templates.
- Ohne `--json`/`--pretty` druckt die CLI nur die **Message** aus dem Template, nicht den rohen HTTP-Body.

---

## CLI-Nutzung

### Install & Discovery

```bash
export MY_API_TOKEN=...

ycallr install ./plugins/ycallr-apis/l/linear.yaml
ycallr --list
ycallr my-api --tree
ycallr my-api --list
```

`ycallr install` erwartet einen **Pfad zur YAML-Datei**, keinen bloßen Profilnamen.

### Commands ausführen

Verschachtelte Commands als **Leerzeichen-getrennte** Pfade (empfohlen in `ycallr-apis`):

```bash
ycallr my-api resources get --id=123 --pretty
ycallr my-api resources items list --owner=OWNER --repo=REPO
```

Alternativ Dot-Notation:

```bash
ycallr my-api resources.items.create --id=123 --title=Bug
```

### Parameter & Output

| Flag | Verhalten |
|------|-----------|
| `--key=value` | Parameter übergeben |
| `--json` | Kompakter JSON-Body |
| `--pretty` | Formatierter JSON-Body |
| `--help` | Command-Hilfe aus kompiliertem Profil |
| `--verbose` / `RUST_LOG=ycallr=debug` | Debug-Logging |

Fehlende required Params: interaktiver Prompt (wenn stdin ein Terminal ist).

### Exit-Codes

| Code | Bedeutung |
|------|-----------|
| 0 | Erfolg |
| 1 | Usage / Client-Fehler |
| 2 | HTTP / API-Fehler |

---

## Workflow: Neuen Pling hinzufügen

### Schritt 1 — API analysieren

- Base-URL und Auth-Schema (Bearer, API-Key, …)
- Welche Env-Vars für Secrets?
- Welche Header sind Pflicht?
- Welche Endpoints zuerst (schrittweise Coverage, kleine Blöcke)?

Offizielle API-Doku ist die beste Quelle. Vorhandene Profile in `plugins/ycallr-apis/` oder `ycallr-core/examples/` als Struktur-Vorlage.

### Schritt 2 — YAML anlegen

```bash
# In plugins/ycallr-apis/ — letter = first character of profile name
touch l/linear.yaml
```

Naming:

- `name:` = CLI-Subcommand = Dateiname ohne Extension
- Verschachtelung spiegelt API-Domäne (z. B. `repos → actions → artifacts → list`)

### Schritt 3 — Validieren und testen

```bash
ycallr install ./my-api.yaml          # Kompilierung + Validierung
ycallr my-api --tree                  # Command-Baum prüfen
ycallr my-api <command> --help        # Params/Endpoint prüfen
ycallr my-api <command> --key=val     # Live-Aufruf
ycallr my-api <command> --pretty      # JSON-Response
```

Install-Fehler kommen aus ycallr-core (strikte Validierung) — YAML korrigieren und erneut installieren.

### Schritt 4 — README dokumentieren

In `plugins/plugins/ycallr-apis/README.md`:

- Profil in Tabelle eintragen
- Auth-Anforderungen
- Beispiel-Commands

### Schritt 5 — Registry (optional, für ReqPack-Distribution)

In `registry/ycallr/packages.json` Eintrag hinzufügen:

```json
{
  "id": "my-api",
  "version": "1.0.0",
  "description": "My API profile for ycallr",
  "tags": ["api", "yaml"],
  "source": {
    "type": "index",
    "url": "https://github.com/Coditary/plugins/ycallr-apis/releases/download/v1.0.0/index.json"
  }
}
```

Nutzer installieren dann über das ReqPack-Ökosystem (`rqp-plugin-ycallr`). Siehe `registry/ycallr/README.md`.

Alternativ direkt per Raw-URL:

```bash
ycallr install https://raw.githubusercontent.com/Coditary/plugins/ycallr-apis/main/l/linear.yaml
```

---

## Workflow: Endpoints zu bestehendem Pling ergänzen

Typischer Ablauf (wie in `plugins/plugins/ycallr-apis/README.md`):

1. Abschnitt in der offiziellen API-Doku wählen.
2. Commands in die passende Verschachtelung im Profil einfügen.
3. `ycallr install <name>.yaml` — Validierung.
4. Manuell testen (`--help`, Live-Call, `--pretty`).
5. README mit neuen Commands aktualisieren.

**Regeln beim Erweitern:**

- Gleiche Auth/Header-Konventionen pro API beibehalten.
- `description` auf jedem Knoten setzen (CLI-Hilfe).
- Sinnvolle `responses.success.message` für Terminal-Output.
- Status-spezifische Fehler in `errors:` nur API-weit, nicht pro Command duplizieren.

---

## OpenAPI-Import (Shortcut)

Statt manuell YAML zu schreiben:

```bash
ycallr import-openapi spec.json --preset my-api
```

Erzeugt ein YAML-Profil aus OpenAPI 3.x. Danach manuell nachbearbeiten (Auth, Messages, Verschachtelung). Details: [OpenAPI Import Wiki](https://github.com/Coditary/ycallr-core/wiki/OpenAPI-Import).

---

## Verteilung & ReqPack

| Artefakt | Zweck |
|----------|-------|
| `.yaml` | Quell-Profil (Git, raw URL, lokaler Pfad) |
| `.pb` | Kompiliertes Profil nach `ycallr install` |
| `.rqp` | ReqPack-Paket für ycallr-CLI-Binary (nicht für einzelne Plings zwingend) |
| `ycallr-registry/ycallr-cli-index.json` | Pinned ReqPack-Index für CLI |
| `registry/ycallr/packages.json` | Katalog für API-Profile und Extensions |

CLI-Releases: [GitHub Releases](https://github.com/Coditary/ycallr-cli/releases) (Linux/macOS `.tar.gz` + `.rqp`, Windows `.zip`).

---

## Wann Rust-Code nötig ist

| Situation | Aktion |
|-----------|--------|
| Neue REST/GraphQL-API anbinden | **Nur YAML** |
| OpenAPI-Spec vorhanden | `import-openapi`, dann YAML feintunen |
| Neuer Auth-Typ / Body-Typ / Validierungsregel | **ycallr-core** |
| CLI-Flags, Prompts, Output-Format | **ycallr-cli** |
| Binding für andere Sprache | C-FFI (`ycallr.h`) — siehe [C FFI Wiki](https://github.com/Coditary/ycallr-core/wiki/C-FFI) |

**Default für Agents:** Erst YAML-Profil. Core/CLI nur wenn das Profilformat die Anforderung nicht abdeckt.

---

## Qualitätskriterien für neue Plings

- [ ] Eindeutiger `name` (klein, stabil, = CLI-Subcommand)
- [ ] `version` und `description` gesetzt
- [ ] Secrets über `env` + `${VAR}`, nicht im Klartext
- [ ] `ycallr install <file>` ohne Fehler
- [ ] `ycallr <name> --tree` zeigt erwartete Struktur
- [ ] Mindestens ein Live-Test pro neuer Leaf-Command
- [ ] Sinnvolle `responses`/`errors`-Messages
- [ ] `plugins/plugins/ycallr-apis/README.md` aktualisiert
- [ ] Optional: Registry-Eintrag in `registry/ycallr/packages.json`

---

## Was Agents vermeiden sollen

- Keine HTTP-Logik in der CLI duplizieren — alles ins YAML-Profil
- Kein zweites Profil-Format erfinden — ycallr-core-Schema ist verbindlich
- Keine Secrets in YAML oder committed `.pb`-Dateien
- Keine flachen Command-Namen wenn die API natürlich verschachtelt ist (`repos actions list` statt `list-repo-action-artifacts`)
- Registry-URLs nicht auf lokale Pfade zeigen — GitHub raw oder Release-URLs
- Nicht `ycallr-core`-Tests überspringen wenn Engine-Verhalten geändert wird

---

## Nützliche Befehle

```bash
# Profil-Workflow
ycallr install ./plugins/ycallr-apis/l/linear.yaml
ycallr --list
ycallr my-api --tree
ycallr my-api health --pretty

# OpenAPI
ycallr import-openapi openapi.json --preset my-api

# Debug
RUST_LOG=ycallr=debug ycallr my-api health --verbose

# Core-Entwicklung (separates Repo)
cd ../ycallr-core && make ci

# CLI-Entwicklung (separates Repo)
cd ../ycallr-cli && cargo build --release
```

---

## Wiki-Kapitel (vertiefend)

| Thema | Link |
|-------|------|
| CLI Home | [ycallr-cli Wiki](https://github.com/Coditary/ycallr-cli/wiki) |
| Commands | [Commands](https://github.com/Coditary/ycallr-cli/wiki/Commands) |
| Installation | [Installation](https://github.com/Coditary/ycallr-cli/wiki/Installation) |
| Output & Options | [Output and Options](https://github.com/Coditary/ycallr-cli/wiki/Output-and-Options) |
| Development (CLI) | [Development](https://github.com/Coditary/ycallr-cli/wiki/Development) |
| ReqPack | [ReqPack](https://github.com/Coditary/ycallr-cli/wiki/ReqPack) |
| API Profiles (Schema) | [API Profiles](https://github.com/Coditary/ycallr-core/wiki/API-Profiles) |
| OpenAPI Import | [OpenAPI Import](https://github.com/Coditary/ycallr-core/wiki/OpenAPI-Import) |
| C FFI | [C FFI](https://github.com/Coditary/ycallr-core/wiki/C-FFI) |

---

## Kurzfassung

ycallr-Plings sind **deklarative API-Beschreibungen in YAML**:

- **Ein Pling** = eine YAML-Datei mit `name`, `base_url`, `auth`, `commands`-Baum
- **Install** kompiliert zu `.pb`; Runtime lädt nur `.pb`
- **CLI** mappt verschachtelte Commands auf Subcommands (`ycallr my-api resources items list …`)
- **Secrets** über Env-Vars; Engine übernimmt HTTP, Auth, Templates
- **Verteilung** über `ycallr-apis` (Git/raw), optional `ycallr-registry` (ReqPack)
- **Kein Rust** für neue APIs — YAML erweitern, installieren, testen, dokumentieren

Ziel: Eine neue API = eine YAML-Datei (+ README + optional Registry) — ohne Änderungen an CLI oder Engine.
