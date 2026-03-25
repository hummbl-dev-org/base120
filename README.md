# Base120

[![CI](https://github.com/hummbl-dev/base120/actions/workflows/ci.yml/badge.svg)](https://github.com/hummbl-dev/base120/actions/workflows/ci.yml)

Base120 is a deterministic governance substrate for system design,
validation,
and execution.

## Authority Statement

This repository is the authoritative reference implementation for Base120 
v1.0.0.
All other language implementations are semantics mirrors and MUST conform 
exactly
to the outputs defined here.

## Contract Unit CLI

Base120 now includes a command-line interface for validating **contract units** - governance artifacts that encapsulate schemas, failure graphs, and version metadata.

**Quick Start:**
```bash
pip install base120
base120 validate-contract path/to/contract.json
```

See [`docs/contract-units.md`](docs/contract-units.md) for complete documentation and examples.

## Canonical Authority

This repository is the authoritative, executable reference for Base120 v1.x.
All other language implementations are semantic mirrors and MUST match the
outputs defined by the golden corpus in `tests/corpus`.

## Versioning

- v1.0.0 — semantic specification freeze
- v1.0.0-post-ci — CI-stabilized, corpus-verified release (recommended)

## Observability

Base120 v1.0.0 includes a **minimal, semantics-preserving observability layer** 
for production deployments. This layer:

- **Emits structured JSON events** for validation success and failure
- **Is opt-in** via an optional `event_sink` parameter (backward compatible)
- **Uses standard library only** (no runtime dependencies)
- **Never affects validation semantics** or determinism

### Quick Start

```python
from base120.validators.validate import validate_artifact
from base120.observability import create_event_sink
import json

# Load schemas and registries
with open("schemas/v1.0.0/artifact.schema.json") as f:
    schema = json.load(f)
with open("registries/mappings.json") as f:
    mappings = json.load(f)
with open("registries/err.json") as f:
    err_registry = json.load(f)["registry"]

# Create event sink (logs to stdout)
event_sink = create_event_sink()

# Validate with observability
artifact = {"id": "test-001", "domain": "core", "class": "example", 
            "instance": "test", "models": ["FM1"]}
errors = validate_artifact(artifact, schema, mappings, err_registry, 
                          event_sink=event_sink)
```

### Event Schema

Each validation emits one `validator_result` event:

```json
{
  "event_type": "validator_result",
  "artifact_id": "artifact-001",
  "schema_version": "v1.0.0",
  "result": "success",
  "error_codes": [],
  "failure_mode_ids": [],
  "timestamp": "2026-01-02T22:15:00.123456Z"
}
```

### Documentation

- **Full specification:** [`docs/observability.md`](docs/observability.md)
- **Event schema:** Fields, guarantees, and integration patterns
- **Governance status:** Part of v1.0.x contract (Indicated work per FM19)

### Backward Compatibility

Omitting `event_sink` (default) preserves original v1.0.0 behavior with no 
observability overhead:

```python
# No events emitted, identical to original v1.0.0
errors = validate_artifact(artifact, schema, mappings, err_registry)
```

This observability layer addresses **FM19 (Observability Failure)** from the 
Base120 governance framework and is production-ready for deployment monitoring.

---

## Governance & Contributing

Base120 implements a **formal governance contract** with automated CI enforcement to ensure:

- **Deterministic validation** across all implementations
- **Mathematical rigor** in formal model changes  
- **Audit trails** for substantive changes
- **Version policy enforcement** (v1.0.x is a frozen specification)

### Quick Links

- **[GOVERNANCE.md](GOVERNANCE.md)** - Complete governance specification
- **[Contributing Guide](docs/governance-migration.md)** - How to submit changes
- **[Decision Tree](docs/governance-decision-tree.md)** - Quick classification reference

### Change Classes

| If you're changing... | Class | Review |
|-----------------------|-------|--------|
| Typos, formatting | Trivial | CODEOWNER only |
| Documentation | Editorial | CODEOWNER only |
| Test corpus | Corpus | CODEOWNER + tests |
| Schemas | Schema | 1+ reviewers |
| Formal models | FM | 2+ reviewers |

See [governance-decision-tree.md](docs/governance-decision-tree.md) for complete classification guide.

### v1.0.x Policy

**Permitted:** Security fixes, CI hardening, documentation, corpus additions  
**Prohibited:** Schema changes, registry modifications, breaking changes

All changes are automatically classified and validated by CI workflows.

## HUMMBL Ecosystem

This repo is part of the [HUMMBL](https://github.com/hummbl-dev) cognitive AI architecture. Related repos:

| Repo | Purpose |
|------|---------|
| [mcp-server](https://github.com/hummbl-dev/mcp-server) | Model Context Protocol server that delivers Base120 models to AI agents |
| [hummbl-governance](https://github.com/hummbl-dev/hummbl-governance) | Governance runtime (kill switch, circuit breaker, cost governor) |
| [arbiter](https://github.com/hummbl-dev/arbiter) | Agent-aware code quality scoring and attribution |
| [agentic-patterns](https://github.com/hummbl-dev/agentic-patterns) | Stdlib-only safety patterns for agentic AI systems |
| [governed-iac-reference](https://github.com/hummbl-dev/governed-iac-reference) | Reference architecture for governed infrastructure-as-code |

Learn more at [hummbl.io](https://hummbl.io).
