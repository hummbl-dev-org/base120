# Base120 Contract Units

> **Status (2026-05-24): archived v1 validator contract.** The current
> `base120` v2 SDK does not implement the `base120 validate-contract` command.
> The CLI examples below document the retired validator surface and must not be
> treated as current package behavior unless validator support is reintroduced
> with tests.

## Overview

Contract units are the **core governance artifacts** in Base120. They serve as **executable specifications** that define:

- **Schemas**: JSON Schema definitions for artifacts (MUST validate artifact structure)
- **Failure Graphs**: Failure mode nodes with retry, escalation, and termination rules (MUST ensure reachable termination)
- **Metadata**: Version information and environment compatibility (MUST include timestamps and environment declarations)

Contract units provide design-time decision surfaces and enable deterministic validation in CI/CD pipelines.

### Relationship to Base120 Global Model

Contract units **govern** how systems implement and validate against the Base120 mental model framework:

- **Domains**: Contract units specify which Base120 domains (e.g., "core", "governance") their artifacts belong to
- **Classes**: The `artifact_schema` defines valid class identifiers that map to Base120 model categories
- **Instances**: Each validated artifact represents a concrete instance within a class
- **Drift Detection**: Contracts provide hooks for detecting when system behavior diverges from model expectations through failure mode tracking

Contract units are **independent governance artifacts** but MUST align with Base120 semantic conventions when referencing domains, classes, and failure modes.

---

## CLI Usage

This section is historical. For current SDK commands, use `base120 list`,
`base120 get`, `base120 prompt`, and `base120 families`.

### Installation

Install Base120 with pip:

```bash
pip install base120
```

### Validating a Contract Unit

Use the `base120 validate-contract` command to validate a contract unit:

```bash
base120 validate-contract <path-to-contract.json>
```

**Options:**
- `-o, --output PATH`: Specify output path for validation report (default: `contract_report.json`)

**Exit Codes:**
- `0`: Validation succeeded
- `1`: Validation failed (errors detected)
- `2`: File not found
- `3`: Invalid JSON syntax
- `4`: File read error
- `5`: Report write error

**Example:**

```bash
base120 validate-contract examples/contracts/valid-basic-contract.json -o report.json
```

---

## Contract Unit Structure

### Required Fields

All contract units **MUST** include the following fields:

1. **`contract_version`** (string, REQUIRED): Version of the contract unit specification
   - Format: `"v{major}.{minor}.{patch}"` (e.g., `"v1.0.0"`)
   - MUST follow semantic versioning

2. **`service_name`** (string, REQUIRED): Unique name of the service this contract governs
   - MUST be non-empty
   - SHOULD be descriptive and globally unique within your organization

3. **`artifact_schema`** (object, REQUIRED): JSON Schema for artifacts validated by this contract
   - MUST include `$schema` field (specifies JSON Schema version)
   - MUST include `type` field (typically `"object"`)
   - SHOULD define properties for `domain`, `class`, and `instance` when integrating with Base120 model
   - Defines the structure and constraints for artifacts this contract validates

4. **`failure_graph`** (object, REQUIRED): Failure mode graph with retry, escalation, and termination rules
   - **`nodes`** (array, REQUIRED): Failure mode nodes in the graph (MUST be non-empty)
   - **`edges`** (array, REQUIRED): Edges between nodes defining escalation paths
   - MUST contain at least one termination node
   - MUST NOT contain cycles (acyclic graph requirement)

5. **`metadata`** (object, REQUIRED): Contract metadata for governance and versioning
   - **`created`** (string, REQUIRED): ISO 8601 timestamp of contract creation
   - **`updated`** (string, REQUIRED): ISO 8601 timestamp of last update
     - MUST be greater than or equal to `created`
   - **`compatibility`** (object, REQUIRED): Environment compatibility information
     - **`environments`** (array, REQUIRED): List of validated environments (MUST be non-empty)
     - **`minimum_version`** (string, OPTIONAL): Minimum contract version required
   - **`description`** (string, RECOMMENDED): Human-readable description of contract purpose
   - **`tags`** (array, RECOMMENDED): Tags for categorization and discoverability

### Normative Language

This specification uses RFC 2119 keywords:
- **MUST**: Absolute requirement (validation fails if not met)
- **MUST NOT**: Absolute prohibition (validation fails if violated)
- **SHOULD**: Strong recommendation (may trigger warnings if not followed)
- **RECOMMENDED**: Suggested best practice (may trigger warnings if not followed)
- **MAY**: Optional (no validation impact)

---

## Failure Graph Specification

### Node Structure

Each node in the failure graph represents a failure mode:

```json
{
  "id": "FM15",
  "name": "Schema Non-Compliance",
  "max_retries": 0,
  "action": "terminate"
}
```

**Fields:**
- **`id`**: Failure mode identifier (format: `FM` followed by digits)
- **`name`**: Human-readable name
- **`max_retries`**: Maximum retry attempts (0-10)
- **`action`**: Action to take (`"retry"`, `"escalate"`, or `"terminate"`)

### Edge Structure

Edges define escalation paths between failure modes:

```json
{
  "from": "FM17",
  "to": "FM30",
  "condition": "max_retries_exceeded"
}
```

**Fields:**
- **`from`**: Source failure mode ID
- **`to`**: Target failure mode ID
- **`condition`**: Condition that triggers the escalation

### Semantic Rules

The validator **MUST** enforce these semantic rules:

1. **Node Uniqueness**: All node IDs MUST be unique within a failure graph
2. **Valid References**: Edge `from` and `to` fields MUST reference existing nodes
3. **Termination Constraint**: Nodes with `action: "terminate"` MUST NOT have outgoing edges
4. **Retry Limits**: `max_retries` MUST be between 0 and 10 (inclusive)
5. **Termination Requirement**: At least one node MUST have `action: "terminate"`
6. **Acyclic Requirement**: The failure graph MUST NOT contain cycles (ensures guaranteed termination)
7. **Datetime Validity**: `created` and `updated` timestamps MUST be valid ISO 8601 format
8. **Temporal Consistency**: `created` timestamp MUST be less than or equal to `updated` timestamp

### Semantic Warnings

The validator **SHOULD** emit warnings (non-blocking) for governance smells:

1. **Missing Description**: Metadata lacks a `description` field
2. **Missing Tags**: Metadata lacks a `tags` field or has an empty tags array
3. **Single Environment**: Contract only declares support for one environment
4. **Unconstrained Models**: Artifact schema's `models` field lacks proper validation constraints

Warnings indicate potential governance issues but do NOT block validation.

---

## Validation Report

The CLI generates a machine-readable JSON report:

```json
{
  "service_name": "user-authentication-service",
  "validation_status": "pass",
  "timestamp": "2026-01-03T17:30:00.123456+00:00",
  "errors": [],
  "warnings": [
    "Metadata: 'description' field is recommended but missing"
  ],
  "compatibility": {
    "validated_environments": ["production", "staging", "development"]
  }
}
```

**Fields:**
- **`service_name`**: Service name from the contract
- **`validation_status`**: `"pass"` or `"fail"`
- **`timestamp`**: ISO 8601 timestamp of validation
- **`errors`**: List of blocking errors (empty if validation passes)
- **`warnings`**: List of non-blocking warnings
- **`compatibility`**: Validated environments from contract metadata

---

## Examples

### Valid Basic Contract

```json
{
  "contract_version": "v1.0.0",
  "service_name": "user-authentication-service",
  "artifact_schema": {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["id", "domain", "class", "instance", "models"],
    "properties": {
      "id": { "type": "string" },
      "domain": { "type": "string" },
      "class": { "type": "string" },
      "instance": { "type": "string" },
      "models": {
        "type": "array",
        "items": { "type": "string" }
      }
    }
  },
  "failure_graph": {
    "nodes": [
      {
        "id": "FM15",
        "name": "Schema Non-Compliance",
        "max_retries": 0,
        "action": "terminate"
      },
      {
        "id": "FM17",
        "name": "Authorization Failure",
        "max_retries": 3,
        "action": "escalate"
      },
      {
        "id": "FM30",
        "name": "Unrecoverable System State",
        "max_retries": 0,
        "action": "terminate"
      }
    ],
    "edges": [
      {
        "from": "FM17",
        "to": "FM30",
        "condition": "max_retries_exceeded"
      }
    ]
  },
  "metadata": {
    "created": "2026-01-03T17:00:00Z",
    "updated": "2026-01-03T17:00:00Z",
    "description": "Contract unit for user authentication service",
    "compatibility": {
      "environments": ["production", "staging", "development"],
      "minimum_version": "v1.0.0"
    },
    "tags": ["authentication", "user-management"]
  }
}
```

### Common Validation Errors

**Error: Missing Required Field**
```
Schema error at 'root': 'metadata' is a required property
```

**Error: Termination Node with Outgoing Edge**
```
Termination node 'FM30' has outgoing edge to 'FM15' (termination nodes cannot escalate)
```

**Error: Invalid Node Reference**
```
Edge 0: 'to' node 'FM99' does not exist
```

**Error: No Termination Node**
```
Failure graph must contain at least one termination node
```

**Error: Cycle Detected**
```
Failure graph contains a cycle: FM1 -> FM2 -> FM1
```

**Error: Invalid Datetime Format**
```
Metadata: 'created' field has invalid datetime format: invalid-date
```

### Common Validation Warnings

**Warning: Missing Description**
```
Metadata: 'description' field is recommended but missing
```

**Warning: Missing Tags**
```
Metadata: 'tags' field is missing or empty (recommended for discoverability)
```

**Warning: Single Environment**
```
Compatibility: Contract only supports a single environment (production). Consider multi-environment support.
```

**Warning: Unconstrained Models**
```
Artifact schema: 'models' items have no constraints (consider defining model validation rules)
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Validate Contract Units

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install Base120
        run: pip install base120
      - name: Validate Contract
        run: base120 validate-contract contracts/service-contract.json
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

for contract in contracts/*.json; do
  echo "Validating $contract..."
  base120 validate-contract "$contract" || exit 1
done
```

---

## Extensibility

The contract unit specification is designed for extensibility. Future versions may add:

- Custom validation rules
- Additional failure graph semantics
- Extended metadata fields
- Artifact provenance tracking
- Cryptographic signatures

All extensions will maintain backward compatibility within the v1.x series.

---

## Mental Model

**Contracts as Governance Artifacts**

Contract units embody the principle that **contracts govern runtime behavior** through explicit, enforceable specifications:

### Lifecycle Phases

1. **Design Time**: Define schemas, failure modes, and policies in contract units
   - Specify Base120 domain alignment (e.g., "core", "governance")
   - Define artifact class identifiers and validation rules
   - Establish failure escalation paths

2. **Validation Time**: Use CLI to validate contracts during development
   - Enforce structural correctness (schema validation)
   - Verify semantic rules (cycles, termination, consistency)
   - Surface governance smells through warnings

3. **Deployment Time**: Bind code and infrastructure to contract constraints
   - Contracts become executable specifications
   - Systems MUST align with contract-defined failure graphs
   - Environment compatibility declarations guide deployment

4. **Runtime**: System behavior conforms to contract specifications
   - Failure modes trigger according to graph definitions
   - Retry and escalation follow contract rules
   - Drift detection compares actual behavior against contract expectations

### Base120 Model Integration

Contract units integrate with the Base120 mental model framework through:

- **Domain Alignment**: Artifacts reference Base120 domains in their schemas
- **Class Mapping**: Contract schemas define which Base120 classes apply
- **Instance Validation**: Each artifact validated is an instance within a class
- **Failure Mode Coverage**: Contracts map system failures to Base120 FM taxonomy

This model ensures that governance decisions are **explicit**, **auditable**, **deterministic**, and **enforceable**.

---

## Governance Status

Contract unit validation is part of Base120 v1.0.x and follows the governance model:

- ✅ **Schema is frozen**: Semantic changes require major version increment
- ✅ **Validation rules are deterministic**: Same input always produces same output
- ✅ **Reports are machine-readable**: JSON format enables automation
- ✅ **Backward compatibility guaranteed**: Within v1.x series
- ✅ **Cycle detection enforced**: Guarantees reachable termination
- ✅ **Datetime validation**: Robust ISO 8601 parsing with timezone support
- ✅ **Semantic warnings**: Non-blocking governance smell detection

For questions or issues, see the [Base120 repository](https://github.com/hummbl-dev/base120).
