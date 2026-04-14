# v1 Python Package — Retirement Notice

**Date**: 2026-04-14  
**Reason**: The v1 Python package violated the HUMMBL stdlib-only invariant (`jsonschema>=4.0`
dependency), used deprecated typing patterns (`from typing import Optional, Dict, Mapping`), and
mixed the FM governance taxonomy (FM1–FM30) with the 120 reasoning operators — two distinct
concepts that should never have shared a package.

## What was removed

- `base120/` — Python package (`cli.py`, `observability.py`, `validators/`, `contract/`, `drift/`)
- `base120.egg-info/` — build artifact
- `tests/` — test suite tied to the retired code

## What remains (source of truth)

| Path | Purpose |
|------|---------|
| `Base120_Canonical_Model_Registry.yaml` | Authoritative definitions for all 120 operators (P/IN/CO/DE/RE/SY × 20) |
| `registries/fm.json` | FM1–FM30 governance failure mode registry |
| `registries/err.json` | Structured error code catalog |
| `registries/mappings.json` | Subclass → FM mappings (40 entries) |
| `docs/`, `schemas/`, `artifacts/` | Research and design material |

## Migration paths

### FM taxonomy (FM1–FM30)
Migrated to `hummbl-governance` v0.4.0:
```python
from hummbl_governance.errors import FailureMode, HummblError, fm_to_errors
from hummbl_governance.failure_modes import get_fm, all_failure_modes
```

### Schema validation
`hummbl-governance` ships a stdlib-only `SchemaValidator` (Draft 2020-12 subset)
that replaces the `jsonschema` dependency:
```python
from hummbl_governance import SchemaValidator
```

### 120 reasoning operators (MCP)
The TypeScript MCP server at `hummbl-research/mcp-server` implements all 120
operators and is the live production implementation. Use it via MCP tool calls.

### Python SDK (v2 — in development)
A new stdlib-only Python SDK is planned with:
- `Engine.apply(code, problem) → ApplyResult`
- `ApplyResult.to_tuple()` — VERUM-aligned `(id, time, state, drift)` evidence tuple
- `base120 apply P6 "..."` CLI
- Zero third-party runtime dependencies
