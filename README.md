# Base120

[![CI](https://github.com/hummbl-dev/base120/actions/workflows/ci.yml/badge.svg)](https://github.com/hummbl-dev/base120/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/base120)](https://pypi.org/project/base120/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue)](LICENSE)
[![v1.0.0](https://img.shields.io/badge/spec-v1.0.0_frozen-orange)]()

**120 mental models for structured reasoning.** Use them to analyze problems, design systems, and make decisions -- whether you are a human, an AI agent, or a fleet of both.

## Quick Example

Apply a model to decompose a problem:

```python
from base120.validators.validate import validate_artifact

# FM42: Separation of Concerns -- does this component have a single responsibility?
artifact = {
    "id": "auth-service-review",
    "domain": "core",
    "class": "architecture",
    "instance": "auth-svc",
    "models": ["FM42"]    # Separation of Concerns
}
errors = validate_artifact(artifact, schema, mappings, err_registry)
# [] -- valid artifact, model applies cleanly
```

Each of the 120 models is a named, versioned reasoning primitive with a defined domain, failure graph, and validation rules.

## Features

- **120 mental models** across 6 cognitive domains (core, systems, security, governance, operations, meta)
- **6 cognitive transformations** -- deterministic operations that compose models into chains
- **CLI validation** -- `base120 validate-contract` checks governance artifacts against the frozen spec
- **Observability layer** -- opt-in structured JSON events for production monitoring
- **MCP integration** -- serve models to AI agents via [mcp-server](https://github.com/hummbl-dev/mcp-server)
- **Golden corpus** -- all implementations must match the canonical test corpus in `tests/corpus`

## Install

```bash
pip install base120

# Or from source
git clone https://github.com/hummbl-dev/base120.git && cd base120
pip install -e ".[test]"
```

## CLI

```bash
# Validate a contract unit (schema, failure graph, version metadata)
base120 validate-contract path/to/contract.json
```

See [`docs/contract-units.md`](docs/contract-units.md) for contract unit format and examples.

## Observability

Opt-in structured events for production deployments:

```python
from base120.observability import create_event_sink

event_sink = create_event_sink()  # logs to stdout
errors = validate_artifact(artifact, schema, mappings, err_registry,
                          event_sink=event_sink)
# Emits: {"event_type": "validator_result", "result": "success", ...}
```

Omitting `event_sink` preserves original v1.0.0 behavior with zero overhead. Full spec: [`docs/observability.md`](docs/observability.md).

## Authority Statement

This repository is the **authoritative reference implementation** for Base120 v1.0.0. All other language implementations are semantic mirrors and MUST conform exactly to the outputs defined here.

### v1.0.x Policy

- **Permitted:** Security fixes, CI hardening, documentation, corpus additions
- **Prohibited:** Schema changes, registry modifications, breaking changes

### Change Classes

| Changing... | Class | Review |
|-------------|-------|--------|
| Typos, formatting | Trivial | CODEOWNER only |
| Documentation | Editorial | CODEOWNER only |
| Test corpus | Corpus | CODEOWNER + tests |
| Schemas | Schema | 1+ reviewers |
| Formal models | FM | 2+ reviewers |

Full governance spec: [GOVERNANCE.md](GOVERNANCE.md) | [Decision tree](docs/governance-decision-tree.md)

## HUMMBL Ecosystem

Part of the [HUMMBL](https://github.com/hummbl-dev) cognitive AI architecture:

- [mcp-server](https://github.com/hummbl-dev/mcp-server) -- Serve Base120 models to Claude and other AI agents
- [hummbl-governance](https://github.com/hummbl-dev/hummbl-governance) -- Governance runtime (kill switch, circuit breaker, cost governor)
- [arbiter](https://github.com/hummbl-dev/arbiter) -- Agent-aware code quality scoring and attribution

Learn more at [hummbl.io](https://hummbl.io).

## License

Apache 2.0 -- see [LICENSE](LICENSE).

---

Built by [HUMMBL LLC](https://hummbl.io). Base120 powers the cognitive layer behind multi-agent coordination at scale.
