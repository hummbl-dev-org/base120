# AGENTS.md — base120

## Project

**base120** — 120 named mental models for structured reasoning across 6 transformation families (Perspective, Inversion, Composition, Decomposition, Recursion, Systems). Stdlib-only Python v2 SDK (`base120` 2.0.0) for operator lookup, prompting, MCP serving, and VERUM-aligned ledger records. Authoritative v1.0.0 reference implementation.

## Scope

- In scope: 120 reasoning operators (P/IN/CO/DE/RE/SY × 20), canonical model registry (`Base120_Canonical_Model_Registry.yaml`), Python SDK (`Engine`, `Ledger`), CLI tooling (`base120 list/get/prompt/families`), append-only JSONL ledger, MCP server (`base120-mcp` entry point), registries and corpus docs
- Out of scope: FM taxonomy FM1–FM30 (migrated to `hummbl-governance` — `from hummbl_governance.errors import FailureMode, HummblError`), TypeScript MCP server (lives in external `mcp-server` mirror)

## Setup

```bash
git clone https://github.com/hummbl-dev/base120.git && cd base120
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
```

## Testing

```bash
python -m pytest tests/ -v
```

Test extras: `pytest>=8.3.4`.

## Conventions

- Python 3.11+ required
- Zero third-party runtime dependencies (stdlib only in production code)
- Each operator is a named, versioned reasoning primitive with a defined transformation family and deterministic package representation
- Canonical registry is the source of truth — frozen v1 reference artifacts remain in-tree
- Commit format: Conventional Commits
- Branch naming: `type/agent/short-desc`
- Apache 2.0 license

## CI

GitHub Actions workflows: `ci.yml`, `base120.yml`, `guardrails.yml`, `mirror-conformance.yml`. Makefile provides local task targets.
