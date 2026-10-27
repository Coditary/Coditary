#!/usr/bin/env python3
"""Normalize top-level env/auth/errors on bulk OpenAPI imports."""
from __future__ import annotations

import re
import sys
from pathlib import Path

PATCHES = {
    "gitlab.yaml": {
        "name": "gitlab",
        "description": "GitLab REST API (full OpenAPI import)",
        "base_url": "https://gitlab.com/api/v4",
        "env": "env:\n  - name: GITLAB_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: api_key
    name: PRIVATE-TOKEN
    in: header
    key: ${GITLAB_TOKEN}
""",
        "errors": """errors:
  default: "GitLab API error {status}: {output.message}"
  401: "Authentication failed — check GITLAB_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the resource may not exist or you cannot access it"
  422: "Invalid request — {output.message}"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [
            (r"auth: apiKey\b", "auth: token"),
            (r"auth: oauth2\b", "auth: token"),
            (r"auth: http\b", "auth: token"),
        ],
    },
    "sentry.yaml": {
        "name": "sentry",
        "description": "Sentry REST API (full OpenAPI import)",
        "base_url": "https://sentry.io",
        "env": "env:\n  - name: SENTRY_AUTH_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${SENTRY_AUTH_TOKEN}
""",
        "errors": """errors:
  default: "Sentry API error {status}: {output.detail}"
  401: "Authentication failed — check SENTRY_AUTH_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the organization, project, issue, or event may not exist"
  400: "Invalid request — {output.detail}"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [(r"auth: auth_token\b", "auth: token")],
    },
    "pagerduty.yaml": {
        "name": "pagerduty",
        "description": "PagerDuty REST API (full OpenAPI import)",
        "base_url": "https://api.pagerduty.com",
        "env": "env:\n  - name: PAGERDUTY_API_KEY\n    required: true\n",
        "auth": """auth:
  token:
    type: http
    scheme: custom
    prefix: "Token token="
    token: ${PAGERDUTY_API_KEY}
""",
        "errors": """errors:
  default: "PagerDuty API error {status}: {output.message}"
  401: "Authentication failed — check PAGERDUTY_API_KEY is set and valid"
  403: "Forbidden — your API key lacks permission for this operation"
  404: "Not found — the resource may not exist or you cannot access it"
  422: "Invalid request — {output.message}"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [(r"auth: api_key\b", "auth: token")],
    },
    "github.yaml": {
        "name": "github",
        "description": "GitHub REST API (full OpenAPI import)",
        "base_url": "https://api.github.com",
        "env": "env:\n  - name: GITHUB_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${GITHUB_TOKEN}
""",
        "errors": """errors:
  default: "GitHub API error {status}: {output.message}"
  401: "Authentication failed — check GITHUB_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the resource may not exist or you cannot access it"
  422: "Invalid request — {output.message}"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [(r"auth: github\b", "auth: token")],
    },
    "dockerhub.yaml": {
        "name": "dockerhub",
        "description": "Docker Hub API (full OpenAPI import)",
        "base_url": "https://hub.docker.com",
        "env": "env:\n  - name: DOCKERHUB_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${DOCKERHUB_TOKEN}
""",
        "errors": """errors:
  default: "Docker Hub API error {status}: {output.message}"
  401: "Authentication failed — check DOCKERHUB_TOKEN (personal access token or JWT)"
  403: "Forbidden — your token cannot access this resource"
  404: "Not found — the resource may not exist or is private"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [
            (r"auth: bearerAuth\b", "auth: token"),
            (r"auth: scimToken\b", "auth: token"),
            (r"auth: bearerSCIMAuth\b", "auth: token"),
        ],
    },
    "vercel.yaml": {
        "name": "vercel",
        "description": "Vercel REST API (full OpenAPI import)",
        "base_url": "https://api.vercel.com",
        "env": "env:\n  - name: VERCEL_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${VERCEL_TOKEN}
""",
        "errors": """errors:
  default: "Vercel API error {status}: {output.error.message}"
  401: "Authentication failed — check VERCEL_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this resource"
  404: "Not found — the resource may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [
            (r"auth: bearerToken\b", "auth: token"),
            (r"auth: oauth2\b", "auth: token"),
        ],
        "inject_auth": True,
    },
    "datadog.yaml": {
        "name": "datadog",
        "description": "Datadog API v2 (full OpenAPI import)",
        "base_url": "https://api.datadoghq.com",
        "env": "env:\n  - name: DD_API_KEY\n    required: true\n  - name: DD_APP_KEY\n    required: true\n",
        "auth": """auth:
  token:
    type: api_key
    name: DD-API-KEY
    in: header
    key: ${DD_API_KEY}
""",
        "errors": """errors:
  default: "Datadog API error {status}: {output.errors}"
  401: "Authentication failed — check DD_API_KEY and DD_APP_KEY are set and valid"
  403: "Forbidden — your API/application keys lack permission for this operation"
  404: "Not found — the resource may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [
            (r"auth: apiKeyAuth\b", "auth: token"),
            (r"auth: appKeyAuth\b", "auth: token"),
            (r"auth: bearerAuth\b", "auth: token"),
            (r"auth: AuthZ\b", "auth: token"),
        ],
        "extra_headers": {"DD-APPLICATION-KEY": "${DD_APP_KEY}"},
    },
    "grafana.yaml": {
        "name": "grafana",
        "description": "Grafana HTTP API (full OpenAPI import — set base_url to your stack URL + /api)",
        "base_url": "https://grafana.example.com/api",
        "env": "env:\n  - name: GRAFANA_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${GRAFANA_TOKEN}
""",
        "errors": """errors:
  default: "Grafana API error {status}: {output.message}"
  401: "Authentication failed — check GRAFANA_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the resource may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [
            (r"auth: basic\b", "auth: token"),
            (r"auth: api_key\b", "auth: token"),
        ],
    },
    "jira.yaml": {
        "name": "jira",
        "description": "Jira Cloud REST API v3 (full OpenAPI import — set base_url to your site)",
        "base_url": "https://your-domain.atlassian.net",
        "env": "env:\n  - name: ATLASSIAN_EMAIL\n    required: true\n  - name: ATLASSIAN_API_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: http
    scheme: basic
    username: ${ATLASSIAN_EMAIL}
    password: ${ATLASSIAN_API_TOKEN}
""",
        "errors": """errors:
  default: "Jira API error {status}: {output.errorMessages}"
  401: "Authentication failed — check ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the issue, project, or resource may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [
            (r"auth: basicAuth\b", "auth: token"),
            (r"auth: OAuth2\b", "auth: token"),
        ],
    },
    "bitbucket.yaml": {
        "name": "bitbucket",
        "description": "Bitbucket Cloud REST API (full OpenAPI import)",
        "base_url": "https://api.bitbucket.org/2.0",
        "env": "env:\n  - name: BITBUCKET_USERNAME\n    required: true\n  - name: BITBUCKET_APP_PASSWORD\n    required: true\n",
        "auth": """auth:
  token:
    type: http
    scheme: basic
    username: ${BITBUCKET_USERNAME}
    password: ${BITBUCKET_APP_PASSWORD}
""",
        "errors": """errors:
  default: "Bitbucket API error {status}: {output.error.message}"
  401: "Authentication failed — check BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD"
  403: "Forbidden — your app password lacks permission for this operation"
  404: "Not found — the repository or resource may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [
            (r"auth: oauth2\b", "auth: token"),
            (r"auth: basic\b", "auth: token"),
            (r"auth: api_key\b", "auth: token"),
        ],
    },
    "circleci.yaml": {
        "name": "circleci",
        "description": "CircleCI API v2 (full OpenAPI import)",
        "base_url": "https://circleci.com/api/v2",
        "env": "env:\n  - name: CIRCLECI_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${CIRCLECI_TOKEN}
""",
        "errors": """errors:
  default: "CircleCI API error {status}: {output.message}"
  401: "Authentication failed — check CIRCLECI_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the pipeline, job, or resource may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [
            (r"auth: api_key_header\b", "auth: token"),
            (r"auth: bearer_auth\b", "auth: token"),
            (r"auth: basic_auth\b", "auth: token"),
            (r"auth: api_key_query\b", "auth: token"),
        ],
    },
    "digitalocean.yaml": {
        "name": "digitalocean",
        "description": "DigitalOcean API v2 (full OpenAPI import)",
        "base_url": "https://api.digitalocean.com",
        "env": "env:\n  - name: DIGITALOCEAN_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${DIGITALOCEAN_TOKEN}
""",
        "errors": """errors:
  default: "DigitalOcean API error {status}: {output.message}"
  401: "Authentication failed — check DIGITALOCEAN_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the droplet or resource may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [(r"auth: bearer_auth\b", "auth: token")],
    },
    "supabase.yaml": {
        "name": "supabase",
        "description": "Supabase Management API (full OpenAPI import)",
        "base_url": "https://api.supabase.com",
        "env": "env:\n  - name: SUPABASE_ACCESS_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${SUPABASE_ACCESS_TOKEN}
""",
        "errors": """errors:
  default: "Supabase API error {status}: {output.message}"
  401: "Authentication failed — check SUPABASE_ACCESS_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the project or resource may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [(r"auth: bearer\b", "auth: token")],
    },
    "terraform.yaml": {
        "name": "terraform",
        "description": "HCP Terraform / Terraform Enterprise API v2 (full OpenAPI import)",
        "base_url": "https://app.terraform.io/api/v2",
        "env": "env:\n  - name: TF_API_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${TF_API_TOKEN}
""",
        "errors": """errors:
  default: "Terraform Cloud API error {status}: {output.errors.0.detail}"
  401: "Authentication failed — check TF_API_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the workspace, run, or resource may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [(r"auth: bearerAuth\b", "auth: token")],
    },
    "netlify.yaml": {
        "name": "netlify",
        "description": "Netlify REST API (full OpenAPI import)",
        "base_url": "https://api.netlify.com/api/v1",
        "env": "env:\n  - name: NETLIFY_AUTH_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${NETLIFY_AUTH_TOKEN}
""",
        "errors": """errors:
  default: "Netlify API error {status}: {output.message}"
  401: "Authentication failed — check NETLIFY_AUTH_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the site or deployment may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [(r"auth: netlifyAuth\b", "auth: token")],
    },
    "fly.yaml": {
        "name": "fly",
        "description": "Fly.io Machines API (full OpenAPI import)",
        "base_url": "https://api.machines.dev",
        "env": "env:\n  - name: FLY_API_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${FLY_API_TOKEN}
""",
        "errors": """errors:
  default: "Fly.io API error {status}: {output.error}"
  401: "Authentication failed — check FLY_API_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the app or machine may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [(r"auth: FlyBearerAuth\b", "auth: token")],
    },
    "render.yaml": {
        "name": "render",
        "description": "Render REST API (full OpenAPI import)",
        "base_url": "https://api.render.com/v1",
        "env": "env:\n  - name: RENDER_API_KEY\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${RENDER_API_KEY}
""",
        "errors": """errors:
  default: "Render API error {status}: {output.message}"
  401: "Authentication failed — check RENDER_API_KEY is set and valid"
  403: "Forbidden — your API key lacks permission for this operation"
  404: "Not found — the service or deployment may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [(r"auth: BearerAuth\b", "auth: token")],
    },
    "railway.yaml": {
        "name": "railway",
        "description": "Railway API (OpenAPI import — mostly GraphQL/OAuth surface)",
        "base_url": "https://backboard.railway.com",
        "env": "env:\n  - name: RAILWAY_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${RAILWAY_TOKEN}
""",
        "errors": """errors:
  default: "Railway API error {status}: {output.message}"
  401: "Authentication failed — check RAILWAY_TOKEN is set and valid"
  403: "Forbidden — your token lacks permission for this operation"
  404: "Not found — the project or resource may not exist"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [
            (r"auth: oauth2\b", "auth: token"),
            (r"auth: apiToken\b", "auth: token"),
        ],
        "inject_auth": True,
    },
    "cloudflare.yaml": {
        "name": "cloudflare",
        "description": "Cloudflare API (full OpenAPI import)",
        "base_url": "https://api.cloudflare.com/client/v4",
        "env": "env:\n  - name: CLOUDFLARE_API_TOKEN\n    required: true\n",
        "auth": """auth:
  token:
    type: bearer
    token: ${CLOUDFLARE_API_TOKEN}
""",
        "errors": """errors:
  default: "Cloudflare API error {status}: {output.errors}"
  401: "Authentication failed — check CLOUDFLARE_API_TOKEN is set and valid"
  403: "Forbidden — your token lacks sufficient scope for this operation"
  404: "Not found — the resource may not exist or you cannot access it"
  422: "Invalid request — {output.errors}"
  429: "Rate limited — retry after the window shown in response headers"
""",
        "auth_replace": [
            (r"auth: api_token\b", "auth: token"),
            (r"auth: api_key\b", "auth: token"),
            (r"auth: api_email\b", "auth: token"),
            (r"auth: user_service_key\b", "auth: token"),
            (r"auth: pages_upload_token\b", "auth: token"),
            (r"auth: assets_jwt\b", "auth: token"),
            (r"auth: default\b", "auth: token"),
            (r"auth: fields\b", "auth: token"),
        ],
    },
}


def patch_file(path: Path, spec: dict) -> None:
    text = path.read_text()
    # Replace auth references in body
    for pattern, repl in spec.get("auth_replace", []):
        text = re.sub(pattern, repl, text)
    if spec.get("inject_auth"):
        text = re.sub(
            r"(\n        method: [^\n]+\n)(?!        auth:)(?=        (?:headers:|params:|body:))",
            r"\1        auth: token\n",
            text,
        )
    extra_headers = spec.get("extra_headers") or {}
    if extra_headers:
        header_lines = "".join(
            f"          {name}: {value}\n" for name, value in extra_headers.items()
        )
        for name in extra_headers:
            text = re.sub(
                rf"(\n        headers:\n)(?!          {re.escape(name)}:)",
                rf"\1{header_lines}",
                text,
            )
        text = re.sub(
            r"(\n        method: [^\n]+\n)(?!        headers:)(?=        (?:params:|body:))",
            rf"\1        headers:\n{header_lines}",
            text,
        )

    # Replace header through start of commands:
    m = re.search(r"^commands:\n", text, re.MULTILINE)
    if not m:
        raise SystemExit(f"commands: not found in {path}")
    version = "1.0.0"
    vm = re.search(r"^version: (.+)\n", text, re.MULTILINE)
    if vm:
        version = vm.group(1).strip().strip("'\"")
    header = (
        f"name: {spec['name']}\n"
        f"version: \"{version}\"\n"
        f"description: {spec['description']}\n"
        f"base_url: {spec['base_url']}\n"
        f"{spec['env']}"
        f"{spec['auth']}"
        f"{spec['errors']}"
        "commands:\n"
    )
    text = header + text[m.end() :]
    # OpenAPI import may append a root-level errors block at EOF; keep only header errors.
    text = re.sub(r"\nerrors:\n(?:  .+\n)+?\Z", "\n", text)
    path.write_text(text)
    print(f"Patched {path}")


def main() -> None:
    root = Path(__file__).resolve().parents[3] / "plugins" / "ycallr-apis"
    files = {
        "g/github.yaml": PATCHES["github.yaml"],
        "g/gitlab.yaml": PATCHES["gitlab.yaml"],
        "s/sentry.yaml": PATCHES["sentry.yaml"],
        "p/pagerduty.yaml": PATCHES["pagerduty.yaml"],
        "c/cloudflare.yaml": PATCHES["cloudflare.yaml"],
        "d/dockerhub.yaml": PATCHES["dockerhub.yaml"],
        "d/datadog.yaml": PATCHES["datadog.yaml"],
        "d/digitalocean.yaml": PATCHES["digitalocean.yaml"],
        "v/vercel.yaml": PATCHES["vercel.yaml"],
        "g/grafana.yaml": PATCHES["grafana.yaml"],
        "j/jira.yaml": PATCHES["jira.yaml"],
        "b/bitbucket.yaml": PATCHES["bitbucket.yaml"],
        "c/circleci.yaml": PATCHES["circleci.yaml"],
        "s/supabase.yaml": PATCHES["supabase.yaml"],
        "t/terraform.yaml": PATCHES["terraform.yaml"],
        "n/netlify.yaml": PATCHES["netlify.yaml"],
        "f/fly.yaml": PATCHES["fly.yaml"],
        "r/render.yaml": PATCHES["render.yaml"],
        "r/railway.yaml": PATCHES["railway.yaml"],
    }
    for rel, spec in files.items():
        path = root / rel
        if path.exists():
            patch_file(path, spec)
        else:
            print(f"Skip missing {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
