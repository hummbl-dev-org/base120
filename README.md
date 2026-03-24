# Base120

[![CI](https://github.com/hummbl-dev/base120/actions/workflows/base120.yml/badge.svg)](https://github.com/hummbl-dev/base120/actions/workflows/base120.yml)
[![Drift Detection](https://github.com/hummbl-dev/base120/actions/workflows/drift-detection.yml/badge.svg)](https://github.com/hummbl-dev/base120/actions/workflows/drift-detection.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

**Base120 is a deterministic governance substrate for system design, validation, and execution.**

It defines 120 executable mental models across 6 transformations (Perspective, Inversion, Composition, Decomposition, Recursion, Synthesis) that encode failure modes, guardrails, and escalation decisions. These models are machine-checkable: you validate artifacts against them before runtime, not after.

This repository is the authoritative v1.0.0 reference implementation. All other language implementations are semantic mirrors and MUST conform exactly to the outputs defined by the golden corpus in `tests/corpus`.

## Quick Start

```bash
pip install -e .
base120 validate-contract path/to/contract.json
```

See [`docs/contract-units.md`](docs/contract-units.md) for complete documentation.

## Structure

```
base120/
  cli.py                 # CLI entry point
  validators/            # Deterministic artifact validation
  contract/              # Contract unit validation
  drift/                 # Semantic drift detection
  observability.py       # Opt-in structured event emission
schemas/v1.0.0/          # Frozen JSON schemas
registries/              # Model mappings and error registry
tests/corpus/            # Golden corpus (conformance suite)
governance/              # CAES spec, version pins, SHA256 hashes
```

## Versioning

| Version | Status | Notes |
|---------|--------|-------|
| v1.0.0 | Frozen | Semantic specification freeze |
| v1.0.0-post-ci | Recommended | CI-stabilized, corpus-verified |

**v1.0.x policy:** Security fixes, CI hardening, documentation, and corpus additions are permitted. Schema changes, registry modifications, and breaking changes are prohibited.

## Observability

Base120 includes a minimal, semantics-preserving observability layer for production deployments:

- Emits structured JSON events for validation success and failure
- Opt-in via `event_sink` parameter (backward compatible)
- Standard library only (no runtime dependencies beyond jsonschema)
- Never affects validation semantics or determinism

```python
from base120.validators.validate import validate_artifact
from base120.observability import create_event_sink

event_sink = create_event_sink()
errors = validate_artifact(artifact, schema, mappings, err_registry,
                          event_sink=event_sink)
```

Omitting `event_sink` preserves original v1.0.0 behavior with zero overhead. See [`docs/observability.md`](docs/observability.md) for the full specification.

## CI

10 workflows enforce governance automatically:

| Workflow | Purpose |
|----------|---------|
| `base120.yml` | Core tests and validation |
| `drift-detection.yml` | Nightly semantic drift check |
| `governance-audit.yml` | Change classification audit |
| `governance-invariants.yml` | Frozen-spec invariant checks |
| `mirror-conformance.yml` | Cross-implementation conformance |
| `guardrails.yml` | PR guardrails |

## Governance

Base120 implements a formal governance contract with automated CI enforcement. See [GOVERNANCE.md](GOVERNANCE.md) for the complete specification.

| Change type | Class | Review required |
|-------------|-------|-----------------|
| Typos, formatting | Trivial | CODEOWNER only |
| Documentation | Editorial | CODEOWNER only |
| Test corpus | Corpus | CODEOWNER + tests |
| Schemas | Schema | 1+ reviewers |
| Formal models | FM | 2+ reviewers |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. The short version: this is a frozen v1.0.x spec, so most contributions are documentation, corpus additions, or CI improvements.

## License

Apache 2.0. See [LICENSE](LICENSE).
