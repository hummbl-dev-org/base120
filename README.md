# Base120

> **v2 SDK active (2026-05-24).** This repository contains the stdlib-only
> Python v2 SDK (`base120` 2.0.0) for operator lookup, prompting, MCP
> serving, and VERUM-aligned ledger records.
> The canonical registry (`Base120_Canonical_Model_Registry.yaml`) and data
> files (`registries/`) remain here as source of truth.
>
> **FM taxonomy (FM1–FM30) migrated to:**
> [`hummbl-governance`](https://github.com/hummbl-dev/hummbl-governance)
> — `from hummbl_governance.errors import FailureMode, HummblError`
>
> **MCP server:** use the Python `base120-mcp` entry point from this package,
> or the external [`mcp-server`](https://github.com/hummbl-dev/mcp-server)
> mirror when a TypeScript server is required.

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue)](LICENSE)
[![Models](https://img.shields.io/badge/models-120-brightgreen)]()
[![Domains](https://img.shields.io/badge/domains-6-blue)]()
[![CI](https://github.com/hummbl-dev/base120/actions/workflows/ci.yml/badge.svg)](https://github.com/hummbl-dev/base120/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Last commit](https://img.shields.io/github/last-commit/hummbl-dev/base120/main)](https://github.com/hummbl-dev/base120/commits/main)

**120 named mental models for structured reasoning.** Use them to analyze problems, design systems, and make decisions — whether you are a human, an AI agent, or a fleet of both.

Learn more at [hummbl.io](https://hummbl.io).

---

## Base120 in 5 Minutes

```bash
git clone https://github.com/hummbl-dev/base120.git
cd base120
```

**Read the canonical registry directly (any language):**

```python
import yaml

with open("Base120_Canonical_Model_Registry.yaml") as f:
    registry = yaml.safe_load(f)

models = {m["id"]: m for m in registry["models"]}
print(models["P1"]["name"])   # → First Principles Framing
print(models["IN6"]["name"])  # → Pre-Mortem
print(models["SY13"]["name"]) # → Reinforcing Feedback
```

**Or use the Python SDK:**

```python
from base120 import Engine

engine = Engine()
operator = engine.get("P6")
print(operator.name)  # → Point-of-View Anchoring
prompt = engine.prompt("P6", "How should we price the certification tier?")
```

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

## The 6 Cognitive Domains

| Domain | Code | Focus | Example Models |
|--------|------|-------|----------------|
| **Perspective** | P | Viewpoints, framing, empathy | P1 First Principles, P5 Empathy Mapping, P10 Context Windowing |
| **Inversion** | IN | Counterfactuals, negation, proof by contradiction | IN1 Reductio ad Absurdum, IN5 Worst-Case Analysis, IN6 Pre-Mortem |
| **Composition** | CO | Building, combining, layering | CO1 Modularity, CO5 Interface Design, CO10 Protocol Layering |
| **Decomposition** | DE | Breaking down, isolating, factoring | DE1 Root Cause Analysis, DE5 Separation of Concerns, DE8 Dimensional Reduction |
| **Recursion** | RE | Self-reference, iteration, meta-reasoning | RE1 Feedback Loop, RE5 Recursion, RE8 Self-Reference |
| **Systems** | SY | Dynamics, emergence, control | SY1 Causal Loop Diagrams, SY13 Homeostasis, SY18 Resilience Engineering |

**Total: 120 models.** Full registry in [`Base120_Canonical_Model_Registry.yaml`](Base120_Canonical_Model_Registry.yaml).

## Example: Structured Decision-Making

**Problem**: "Should we migrate from REST to GraphQL?"

```
Step 1 — P1 (First Principles):
  What are the irreducible requirements? Latency, cacheability, client flexibility.

Step 2 — IN5 (Worst-Case Analysis):
  What if the migration takes 6 months and breaks mobile clients?

Step 3 — DE5 (Separation of Concerns):
  Which parts of the API actually need flexibility? Read paths vs write paths.

Step 4 — CO1 (Modularity):
  Can we support both during transition? BFF pattern, not big-bang.

Step 5 — SY13 (Feedback Loops):
  How do we know it's working? Metrics: latency p99, error rate, client adoption.
```

Each step names the model, applies it, and passes output to the next. No vague advice — explicit reasoning with receipts.

## The 120 Models (Abbreviated)

<details>
<summary>Click to expand full model list</summary>

### Domain P — Perspective (P1–P18)
P1 First Principles Framing | P2 Stakeholder Mapping | P3 Identity Stack | P4 Lens Shifting | P5 Empathy Mapping | P6 Point-of-View Anchoring | P7 Perspective Switching | P8 Narrative Framing | P9 Cultural Lens Shifting | P10 Context Windowing | P11 Role Perspective-Taking | P12 Temporal Framing | P13 Spatial Framing | P14 Reference Class Framing | P15 Assumption Surfacing | P16 Identity-Context Reciprocity | P17 Frame Control & Reframing | P18 Horizon Scanning

### Domain IN — Inversion (IN1–IN18)
IN1 Reductio ad Absurdum | IN2 Proof by Contradiction | IN3 Negation Testing | IN4 Counterfactual Reasoning | IN5 Worst-Case Analysis | IN6 Pre-Mortem | IN7 Regret Minimization | IN8 Inversion Principle | IN9 Constraint Relaxation | IN10 Opposite Thinking | IN11 Devil's Advocate | IN12 Second-Order Negation | IN13 Assumption Violation | IN14 Boundary Stressing | IN15 Failure Mode Enumeration | IN16 Adversarial Generation | IN17 Exclusion Analysis | IN18 Complement Thinking

### Domain CO — Composition (CO1–CO20)
CO1 Modularity | CO2 Abstraction | CO3 Encapsulation | CO4 Interface Design | CO5 Protocol Layering | CO6 Dependency Injection | CO7 Pipeline Construction | CO8 Orchestration | CO9 Service Composition | CO10 Microservice Decomposition | CO11 Event-Driven Architecture | CO12 API Gateway Pattern | CO13 Federation | CO14 Polyglot Persistence | CO15 CQRS | CO16 Event Sourcing | CO17 Saga Pattern | CO18 Strangler Fig Pattern | CO19 Sidecar Pattern | CO20 Ambassador Pattern

### Domain DE — Decomposition (DE1–DE20)
DE1 Root Cause Analysis | DE2 Five Whys | DE3 Fault Tree Analysis | DE4 Fishbone Diagram | DE5 Separation of Concerns | DE6 Dimensional Reduction | DE7 Factor Analysis | DE8 Principal Component Analysis | DE9 Feature Extraction | DE10 Domain-Driven Design | DE11 Bounded Context | DE12 Aggregate Decomposition | DE13 Entity-Relationship Modeling | DE14 Normalization | DE15 Refactoring | DE16 Extract Method | DE17 Decompose Conditional | DE18 Replace Inheritance | DE19 Split Phase | DE20 Replace Algorithm

### Domain RE — Recursion (RE1–RE20)
RE1 Feedback Loop | RE2 Recursion | RE3 Iteration | RE4 Self-Reference | RE5 Meta-Reasoning | RE6 Reflection | RE7 Introspection | RE8 Bootstrapping | RE9 Self-Modification | RE10 Auto-Tuning | RE11 Meta-Learning | RE12 Transfer Learning | RE13 Curriculum Learning | RE14 Active Learning | RE15 Reinforcement Learning | RE16 Q-Learning | RE17 Policy Gradient | RE18 Actor-Critic | RE19 Multi-Agent Reinforcement | RE20 Hierarchical Reinforcement

### Domain SY — Systems (SY1–SY24)
SY1 Causal Loop Diagrams | SY2 Stock and Flow | SY3 Systems Archetypes | SY4 Leverage Points | SY5 Tragedy of the Commons | SY6 Fixes That Fail | SY7 Shifting the Burden | SY8 Eroding Goals | SY9 Escalation | SY10 Success to the Successful | SY11 Limits to Growth | SY12 Balancing Feedback | SY13 Reinforcing Feedback | SY14 Homeostasis | SY15 Resilience | SY16 Antifragility | SY17 Optionality | SY18 Redundancy | SY19 Diversity | SY20 Modularity | SY21 Scalability | SY22 Evolvability | SY23 Adaptability | SY24 Robustness

</details>

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
- [hummbl-agent](https://github.com/hummbl-dev/hummbl-agent) -- Governed control plane for AI agent systems
- [hummbl-bibliography](https://github.com/hummbl-dev/hummbl-bibliography) -- Bibliography for the HUMMBL cognitive framework
- [founder-mode-showcase](https://github.com/hummbl-dev/founder-mode-showcase) -- 5-minute demo of the full HUMMBL mesh

Learn more at [hummbl.io](https://hummbl.io).

## License

Apache 2.0 -- see [LICENSE](LICENSE).

---

Built by [HUMMBL LLC](https://hummbl.io). Base120 powers the cognitive layer behind multi-agent coordination at scale.

## Repository Health

See [docs/REPO_HEALTH.md](docs/REPO_HEALTH.md) for validation and branch-protection expectations.
