# Base120

> **Lifecycle note (2026-05-24).** The original v1 validator runtime was
> retired on 2026-04-14. This repository now contains the active stdlib-only
> Python v2 SDK (`base120` 2.0.0.dev0) for operator lookup, prompting, MCP
> serving, and VERUM-aligned ledger records.
> The canonical v1 registry (`Base120_Canonical_Model_Registry.yaml`) and data
> files (`registries/`) remain here as source of truth.
>
> **FM taxonomy (FM1–FM30) migrated to:**
> [`hummbl-governance`](https://github.com/hummbl-research/hummbl-governance)
> — `from hummbl_governance.errors import FailureMode, HummblError`
>
> **MCP server:** use the Python `base120-mcp` entry point from this package,
> or the external [`mcp-server`](https://github.com/hummbl-research/mcp-server)
> mirror when a TypeScript server is required.

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue)](LICENSE)

**120 mental models for structured reasoning.** Use them to analyze problems, design systems, and make decisions — whether you are a human, an AI agent, or a fleet of both.

## Quick Example

Apply an operator, generate a prompt, and persist a governance-readable record:

```python
from base120 import Engine, Ledger

engine = Engine()

operator = engine.get("P6")
print(operator.name)  # Point-of-View Anchoring

prompt = engine.prompt("P6", "How should we price the certification tier?")
result = engine.record(
    "P6",
    "How should we price the certification tier?",
    "Anchor the offer to the compliance officer's risk budget.",
    0.85,
)

ledger = Ledger("base120-ledger.jsonl")
ledger.append(result.to_tuple())
```

Each of the 120 operators is a named, versioned reasoning primitive with a
defined transformation family and deterministic package representation.

## Features

- **120 reasoning operators** across 6 transformation families
- **Stdlib-only Python SDK** -- no third-party runtime dependencies
- **CLI tooling** -- `base120 list`, `base120 get`, `base120 prompt`, and `base120 families`
- **Append-only ledger** -- persist operator applications as VERUM-aligned JSONL tuples
- **MCP integration** -- serve operators to AI agents with the `base120-mcp` entry point
- **Canonical registry and corpus docs** -- frozen v1 reference artifacts remain in-tree

## Install From Source

```bash
git clone https://github.com/hummbl-dev/base120.git && cd base120
pip install -e ".[test]"
```

The package name is `base120`, but this repository should not claim PyPI
availability until a published package exists.

## CLI

```bash
# List all operators
base120 list

# Inspect one operator
base120 get P6

# Generate an operator-specific prompt for a problem
base120 prompt P6 "How should we price the certification tier?"

# List canonical operator families
base120 families
```

The historical contract-unit validator spec is archived in
[`docs/contract-units.md`](docs/contract-units.md); the current v2 SDK does not
ship `base120 validate-contract`.

## Ledger

Persist operator applications as JSONL tuples:

```python
from base120 import Engine, Ledger

engine = Engine()
result = engine.record("DE1", "Reduce release risk.", "Split blockers by owner.", 0.9)

ledger = Ledger()
ledger.append(result.to_tuple())
high_drift = ledger.cut(0.5)
```

The archived v1 validator observability contract remains in
[`docs/observability.md`](docs/observability.md), but the current v2 SDK does
not expose `base120.observability`.

## Authority Statement

This repository is the **authoritative source** for the Base120 v1 registry,
reference artifacts, and current Python v2 SDK. Other language
implementations should conform to the frozen registry and corpus artifacts
defined here. The `2.0.0.dev0` Python SDK API remains pre-release until a
non-dev package version is published.

### v1 Artifact Policy

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

Repository health contract: [docs/REPO_HEALTH.md](docs/REPO_HEALTH.md)

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

## Repository Health

See [docs/REPO_HEALTH.md](docs/REPO_HEALTH.md) for validation and branch-protection expectations.
