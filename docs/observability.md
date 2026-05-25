# Base120 Observability Contract

**Version:** v1.0.0
**Status:** Archived v1 validator contract
**Failure Mode Addressed:** FM19 (Observability Failure)

> **Current SDK note (2026-05-24):** the `base120` v2 SDK does not expose
> `base120.validators` or `base120.observability`. This document preserves the
> retired v1 validator observability contract; it is not a current package API
> promise.

---

## Purpose

This document defines the **minimal, semantics-preserving observability layer** for Base120 validators. It specifies the event schema, emission guarantees, and integration patterns for production deployments.

**Key Principles:**
- Observability is **opt-in** and backward-compatible
- Event emission does **not** affect validation semantics or determinism
- Uses **standard library only** (no runtime dependencies)
- Events are **structured, machine-readable** logs

---

## Event Schema

All Base120 validator events conform to this canonical schema:

```json
{
  "event_type": "validator_result",
  "artifact_id": "artifact-valid-001",
  "schema_version": "v1.0.0",
  "result": "success",
  "error_codes": [],
  "failure_mode_ids": [],
  "timestamp": "2026-01-02T22:15:00.123456Z",
  "correlation_id": "req-12345"
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_type` | string | Yes | Always `"validator_result"` for validation events |
| `artifact_id` | string | Yes | Value of artifact's `id` field, or `"unknown"` if missing |
| `schema_version` | string | Yes | Base120 schema version used (e.g., `"v1.0.0"`) |
| `result` | string | Yes | `"success"` (no errors) or `"failure"` (errors present) |
| `error_codes` | array[string] | Yes | List of error codes returned by validator (e.g., `["ERR-SCHEMA-001"]`) |
| `failure_mode_ids` | array[string] | Yes | List of failure modes resolved during validation (e.g., `["FM15", "FM29"]`) |
| `timestamp` | string | Yes | ISO 8601 timestamp in UTC (RFC 3339 format) |
| `correlation_id` | string | No | Optional request tracing ID passed by consumer |

### Event Types

#### Success Event
```json
{
  "event_type": "validator_result",
  "artifact_id": "artifact-valid-001",
  "schema_version": "v1.0.0",
  "result": "success",
  "error_codes": [],
  "failure_mode_ids": [],
  "timestamp": "2026-01-02T22:15:00.123456Z"
}
```

#### Failure Event (Schema Validation)
```json
{
  "event_type": "validator_result",
  "artifact_id": "artifact-invalid-001",
  "schema_version": "v1.0.0",
  "result": "failure",
  "error_codes": ["ERR-SCHEMA-001"],
  "failure_mode_ids": ["FM15"],
  "timestamp": "2026-01-02T22:15:01.234567Z"
}
```

#### Failure Event (FM30 Dominance)
```json
{
  "event_type": "validator_result",
  "artifact_id": "artifact-gov-001",
  "schema_version": "v1.0.0",
  "result": "failure",
  "error_codes": ["ERR-GOV-004"],
  "failure_mode_ids": ["FM30"],
  "timestamp": "2026-01-02T22:15:02.345678Z"
}
```

---

## Integration Patterns

### Basic Usage (Opt-In)

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

# Create event sink (logs to stdout as structured JSON)
event_sink = create_event_sink()

# Validate with observability
artifact = {"id": "test-001", "domain": "core", "class": "example", "instance": "test"}
errors = validate_artifact(
    artifact, 
    schema, 
    mappings, 
    err_registry,
    event_sink=event_sink
)
```

### Custom Event Handling

```python
def custom_event_handler(event):
    """Send events to observability backend"""
    # Example: send to metrics system
    if event["result"] == "failure":
        metrics.increment("base120.validation.failure", 
                         tags={"error": event["error_codes"][0]})
    
    # Example: send to structured logging
    logger.info("validation_complete", extra=event)

errors = validate_artifact(
    artifact, 
    schema, 
    mappings, 
    err_registry,
    event_sink=custom_event_handler
)
```

### Correlation ID Tracking

```python
# Pass correlation_id through validation context
def validate_with_correlation(artifact, correlation_id):
    def correlated_sink(event):
        event["correlation_id"] = correlation_id
        # Send to your observability system
        log_event(event)
    
    return validate_artifact(
        artifact, 
        schema, 
        mappings, 
        err_registry,
        event_sink=correlated_sink
    )

errors = validate_with_correlation(artifact, "req-12345")
```

### Disable Observability (Default)

```python
# Without event_sink parameter, no events are emitted (backward compatible)
errors = validate_artifact(artifact, schema, mappings, err_registry)
# No side effects, validation behavior unchanged
```

---

## Guarantees

### Semantic Preservation
- Event emission **does not** modify validation results
- Events are emitted **after** validation completes
- Errors in event emission do **not** propagate to caller
- Determinism of validation is **unaffected**

### Backward Compatibility
- `event_sink` parameter is optional (defaults to `None`)
- Existing code without `event_sink` behaves identically to v1.0.0
- No new runtime dependencies required

### Event Consistency
- Exactly **one** `validator_result` event per validation call
- Event timestamp precision: microseconds (ISO 8601 UTC)
- `failure_mode_ids` are always sorted lexicographically
- `error_codes` match validator return value exactly

### Performance
- Event emission adds < 1ms overhead (stdlib JSON serialization)
- No blocking I/O in default implementation
- Event sink failures are caught and logged, never propagate

---

## Failure Mode Mapping

This observability layer addresses **FM19 (Observability Failure)** from COMMIT_AUDIT_BASE120_VIEW.md:

> **FM19: Observability Failure**  
> **Rationale:** Validators emit no events; consumers have no visibility into validation flow or error context  
> **Dimension:** Observability  
> **Control Required:** Define minimal event schema: validation start, schema fail, FM resolution, error emission

### Resolution
- ✅ Event schema defined with explicit fields
- ✅ Success and failure events documented
- ✅ Failure mode IDs included in events
- ✅ Integration patterns for production use
- ✅ Governance guarantee (part of v1.0.x contract)

---

## Governance Status

**Classification:** Indicated work (COMMIT_AUDIT_BASE120_VIEW.md Phase 2)

**Rationale:**
- Does not change v1.0.0 validator semantics
- Backward compatible (opt-in via parameter)
- No new runtime dependencies
- Improves production readiness without affecting determinism

**Approval:** This observability contract is part of Base120's governance guarantees. Consumers can rely on this event schema remaining stable within v1.0.x.

---

## Standard Library Implementation

The reference implementation uses only Python standard library:

```python
import json
import sys
from datetime import datetime, timezone

def create_event_sink(output=sys.stdout):
    """Create a standard event sink that logs to stdout as JSON."""
    def sink(event):
        try:
            json.dump(event, output)
            output.write('\n')
            output.flush()
        except Exception:
            # Never propagate event emission errors
            pass
    return sink
```

Consumers can:
- Use `create_event_sink()` for stdout logging
- Provide custom callables for integration with monitoring systems
- Omit `event_sink` entirely for no observability overhead

---

## Examples

### Production Deployment with DataDog

```python
from datadog import statsd

def datadog_sink(event):
    statsd.increment(
        'base120.validation',
        tags=[
            f"result:{event['result']}",
            f"schema:{event['schema_version']}"
        ]
    )
    if event['result'] == 'failure':
        for error_code in event['error_codes']:
            statsd.increment('base120.error', tags=[f"code:{error_code}"])

errors = validate_artifact(
    artifact, schema, mappings, err_registry,
    event_sink=datadog_sink
)
```

### Audit Trail with Structured Logging

```python
import logging
import json

logger = logging.getLogger('base120.audit')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('/var/log/base120-audit.log')
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)

def audit_sink(event):
    logger.info(json.dumps(event))

errors = validate_artifact(
    artifact, schema, mappings, err_registry,
    event_sink=audit_sink
)
```

---

## Testing Contract

The observability layer is validated by tests in `tests/test_observability.py`:

- ✅ Success validation emits event with `result: "success"`
- ✅ Failure validation emits event with error codes and failure mode IDs
- ✅ Schema validation failure includes FM15 in failure_mode_ids
- ✅ FM30 dominance reflected in failure_mode_ids
- ✅ Event emission errors do not propagate
- ✅ Omitting event_sink preserves original behavior
- 
### Deterministic Timestamp Testing

For tests that require deterministic behavior (e.g., Golden Corpus validation, hash verification), the observability layer supports a fixed timestamp mode via the `BASE120_FIXED_TIMESTAMP` environment variable:

```bash
# Set a fixed timestamp for deterministic observability events
export BASE120_FIXED_TIMESTAMP="2026-01-01T00:00:00.000000Z"

# Run tests - all observability events will use this timestamp
pytest tests/test_corpus.py
```

**Use Cases:**

- ✅ **CI Determinism Checks**: Ensure identical outputs across multiple test runs (e.g., `.github/workflows/governance-invariants.yml`)
- - ✅ **Hash Verification**: Validate that corpus outputs produce consistent hashes when timestamps are fixed
  - - ✅ **Regression Testing**: Compare observability outputs across versions without timestamp drift
    - - ✅ **Local Development**: Reproduce CI test conditions locally for debugging
     
      - **Behavior:**
     
      - - When `BASE120_FIXED_TIMESTAMP` is set, all observability events use this timestamp instead of the current time
        - - When unset (default), observability events use dynamic timestamps (`datetime.now(timezone.utc)`)
          - - Production code is **unaffected** - only timestamp emission changes, validation semantics remain identical
            - - Tests verify both fixed and dynamic timestamp behavior (`test_deterministic_timestamp_via_env_var()`, `test_dynamic_timestamp_without_env_var()`)
             
              - This pattern enables governance-enforced determinism checks (Invariant 1: Golden Corpus Determinism) while preserving the opt-in, backward-compatible observability design.

---

## Version History

- **v1.0.0** - Initial observability contract (2026-01-02)

---

**Document Status:** Active governance artifact  
**Next Review:** v1.1.0 planning or governance escalation
