# Base120 Mirror Conformance Contract

## Overview

This document defines the **enforceable conformance contract** for Base120 language mirror implementations. Mirror conformance is **infrastructure-enforced, not advisory or optional**.

**Authority:** The Python implementation at `hummbl-dev/base120` is the canonical reference. All mirror implementations MUST produce **byte-for-byte identical outputs** for all golden corpus test cases.

**Key Principles:**
- **Deterministic Validation**: All implementations must produce identical error outputs
- **Corpus-Driven Correctness**: The golden corpus defines correctness
- **Automated Verification**: CI enforces conformance before certification
- **Lifecycle Management**: Mirrors progress through formal states with clear criteria

---

## Golden Corpus Conformance

### Definition

A mirror implementation is **conformant** if and only if:

```
∀ artifact A in golden corpus:
  validate_mirror(A) == validate_canonical(A)  [byte-for-byte]
```

The golden corpus resides in the canonical repository at:
- `tests/corpus/valid/*.json` → MUST produce empty error list `[]`
- `tests/corpus/invalid/*.json` → MUST produce error list matching `tests/corpus/expected/*.errs.json`

### Corpus Structure

**Valid Artifacts** (`tests/corpus/valid/`):
- Each file is a valid Base120 artifact
- Validation MUST return empty error list `[]`
- Adding valid corpus: allowed (with audit)
- Modifying valid corpus: PROHIBITED in v1.0.x

**Invalid Artifacts** (`tests/corpus/invalid/`):
- Each file is an invalid Base120 artifact
- Validation MUST return errors matching expected output

**Expected Errors** (`tests/corpus/expected/`):
- Each `<name>.errs.json` contains expected error array for `invalid/<name>.json`
- Errors are sorted lexicographically by error code
- Format: JSON array of error code strings, e.g., `["ERR-SCHEMA-001"]`

### Byte-for-Byte Identity

**Canonical Serialization Rules:**
1. **JSON Output**: UTF-8 encoding, sorted object keys, no insignificant whitespace
2. **Error Arrays**: Lexicographically sorted by error code string
3. **No Timestamps**: No dynamic timestamps in error output (use `BASE120_FIXED_TIMESTAMP` for testing)
4. **No Randomness**: No UUIDs, random values, or environment-dependent data
5. **Deduplication**: Error codes deduplicated before sorting

**Example:**
```json
["ERR-SCHEMA-001"]
```

NOT:
```json
[ "ERR-SCHEMA-001" ]
```

---

## Mirror Lifecycle States

All mirror implementations progress through formal lifecycle states with defined entry/exit criteria.

### State 1: Draft

**Definition:** Work in progress, not yet validated against corpus.

**Entry Criteria:**
- Repository created
- Basic implementation started

**Requirements:**
- None (exploratory phase)

**Exit Criteria:**
- Implementation complete enough for corpus validation
- Developer declares intent to move to Review state

**Duration:** Unlimited

---

### State 2: Review

**Definition:** Under evaluation for conformance, validation in progress.

**Entry Criteria:**
- Core validation pipeline implemented
- Ready for corpus testing

**Requirements:**
- Implement validation logic equivalent to canonical implementation
- Set up CI with mirror conformance workflow (see [Workflow Integration](#workflow-integration))
- Run corpus validation against all golden corpus artifacts
- Document any deviations or issues

**Exit Criteria to Approved:**
- **ALL** golden corpus tests pass (100% conformance)
- CI workflow passes cleanly
- Documentation complete (README, usage examples)
- At least 1 external review confirming conformance

**Exit Criteria to Draft (rejected):**
- Fundamental architectural issues discovered
- Unable to achieve conformance
- Developer abandons effort

**Duration:** Typically 1-4 weeks

---

### State 3: Approved

**Definition:** Certified conformant mirror, approved for production use.

**Entry Criteria:**
- 100% golden corpus conformance verified
- CI workflow integrated and passing
- External review completed
- Documentation complete

**Requirements:**
- MUST maintain 100% conformance across updates
- MUST run conformance CI on every PR
- MUST update when canonical corpus changes
- MUST document any known limitations

**Maintenance:**
- Monitor canonical repository for corpus changes
- Update implementation to maintain conformance
- Re-run conformance validation after any changes

**Exit Criteria to Deprecated:**
- Maintainer declares deprecation
- Persistent conformance failures
- Security issues discovered

**Duration:** Indefinite (while maintained)

---

### State 4: Deprecated

**Definition:** No longer recommended, but still functional.

**Entry Criteria:**
- Maintainer deprecates mirror
- Persistent conformance failures
- Security issues without fix

**Requirements:**
- Mark as deprecated in README
- Provide migration guidance to other mirrors
- Document deprecation reason
- Optionally maintain security fixes

**Exit Criteria to Removed:**
- Sufficient time for migration (minimum 3 months)
- Governance approval for removal

**Duration:** Minimum 3 months

---

### State 5: Removed

**Definition:** Delisted from official mirrors, no longer supported.

**Entry Criteria:**
- Governance approval
- Migration period completed
- No active users (or users notified)

**Requirements:**
- Archive repository (make read-only)
- Update canonical mirrors/README.md to remove listing
- Preserve historical record

**Duration:** Permanent

---

## Corpus Diff Validation Criteria

### Passing Criteria

A mirror implementation **PASSES** corpus validation if:

1. **All Valid Tests Pass**:
   - Every artifact in `tests/corpus/valid/` returns `[]`
   - No false positives

2. **All Invalid Tests Match**:
   - Every artifact in `tests/corpus/invalid/` returns exact error list
   - Errors match `tests/corpus/expected/<name>.errs.json` byte-for-byte
   - Error order is lexicographically sorted

3. **Determinism Verified**:
   - Running tests 3 times produces identical output
   - No non-deterministic behavior

4. **No Extra/Missing Errors**:
   - Error count matches expected exactly
   - No additional errors beyond expected
   - No missing errors from expected

### Failure Modes

A mirror implementation **FAILS** if:

- **False Positive**: Valid artifact produces errors
- **False Negative**: Invalid artifact produces `[]` or wrong errors
- **Wrong Errors**: Error codes differ from expected
- **Wrong Order**: Errors not sorted lexicographically
- **Non-Determinism**: Different outputs across runs
- **Extra Errors**: More errors than expected
- **Missing Errors**: Fewer errors than expected

### Diff Output Format

When conformance fails, the CI workflow produces a detailed diff:

```
❌ FAIL: Corpus validation failed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Valid Corpus Results: 3/4 passed (75.0%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ valid-basic.json
✅ valid-example-2.json
✅ valid-example-3.json
❌ valid-example-4.json
   Expected: []
   Got: ["ERR-SCHEMA-001"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Invalid Corpus Results: 2/3 passed (66.7%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ invalid-schema-missing-field.json
✅ invalid-governance-unrecoverable.json
❌ invalid-recovery-plus-unrecoverable.json
   Expected: ["ERR-FM30-001"]
   Got: ["ERR-FM30-001", "ERR-FM15-001"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall: 5/7 tests passed (71.4%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To fix:
1. Review failing test cases
2. Compare your implementation against canonical behavior
3. Fix validation logic
4. Re-run conformance workflow
```

---

## Workflow Integration

### For Mirror Repositories

Mirror implementations MUST integrate the reusable conformance workflow to automate validation.

#### Step 1: Add Workflow File

Create `.github/workflows/conformance.yml` in your mirror repository:

```yaml
name: Base120 Mirror Conformance

on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  validate-conformance:
    uses: hummbl-dev/base120/.github/workflows/mirror-conformance.yml@main
    with:
      # Language/runtime for your mirror
      language: 'javascript'  # or 'typescript', 'go', 'rust', etc.
      
      # Command to run your validator against a single artifact JSON file
      # The workflow will pass the artifact path as an argument
      # Your validator MUST output error array JSON to stdout
      validate-command: 'node dist/validate.js'
      
      # Optional: Setup command (install dependencies, build, etc.)
      setup-command: 'npm install && npm run build'
```

#### Step 2: Implement Validator CLI

Your mirror MUST provide a CLI that:

1. **Input**: Accepts artifact JSON file path as argument
2. **Output**: Writes error array JSON to stdout
3. **Format**: Matches canonical format exactly

Example invocation:
```bash
$ node dist/validate.js tests/corpus/valid/valid-basic.json
[]

$ node dist/validate.js tests/corpus/invalid/invalid-schema-missing-field.json
["ERR-SCHEMA-001"]
```

#### Step 3: Determinism

Set `BASE120_FIXED_TIMESTAMP` environment variable for deterministic testing:

```bash
BASE120_FIXED_TIMESTAMP="2026-01-01T00:00:00.000000Z" node dist/validate.js artifact.json
```

Your implementation MUST respect this environment variable if it generates any timestamp-based data.

**Language-Agnostic Note**: This environment variable should be respected by all mirror implementations regardless of programming language. Check for its presence at runtime and use the provided timestamp instead of generating dynamic timestamps.

---

## Certification Process

### Prerequisites

Before requesting certification:

1. ✅ Implementation complete
2. ✅ CI workflow integrated
3. ✅ All golden corpus tests pass locally
4. ✅ Documentation complete (README, usage examples)
5. ✅ License compatible (MIT, Apache 2.0, or similar)

### Certification Steps

**Step 1: Self-Assessment**

Run the conformance workflow locally and verify 100% pass rate:

```bash
# Clone canonical corpus
git clone https://github.com/hummbl-dev/base120
cd base120

# Copy corpus to your mirror
cp -r tests/corpus /path/to/your/mirror/tests/

# Run your validator against corpus
# (implementation-specific)
```

**Step 2: Request Review**

1. Open an issue in `hummbl-dev/base120` repository
2. Use title: `[Mirror Certification] <language> Implementation`
3. Include:
   - Link to mirror repository
   - CI workflow status badge
   - Conformance test results
   - Usage documentation

**Step 3: External Review**

- At least 1 external reviewer validates conformance
- Reviewer runs CI workflow
- Reviewer checks documentation
- Reviewer confirms output matches canonical

**Step 4: Approval**

- Reviewer approves via GitHub issue
- Mirror added to `mirrors/README.md` as **Approved**
- Announcement in canonical repository
- Badge/certification mark available

### Maintaining Certification

**Ongoing Requirements:**
- CI conformance checks MUST run on every PR
- Maintainer MUST respond to conformance failures within 7 days
- Maintainer MUST update when canonical corpus changes
- Maintainer MUST document any known issues

**Re-certification Triggers:**
- Major version updates to mirror
- Changes to golden corpus
- Conformance failures persisting >30 days
- Security issues discovered

---

## Examples

### Example 1: Valid Artifact

**Input** (`tests/corpus/valid/valid-basic.json`):
```json
{
  "id": "artifact-valid-001",
  "domain": "core",
  "class": "example",
  "instance": "happy-path",
  "models": ["FM1"]
}
```

**Expected Output:**
```json
[]
```

**Mirror Implementation Must:**
- Parse JSON successfully
- Validate against schema
- Return empty array (no errors)

---

### Example 2: Invalid Artifact (Schema Violation)

**Input** (`tests/corpus/invalid/invalid-schema-missing-field.json`):
```json
{
  "id": "artifact-invalid-001",
  "domain": "core",
  "class": "example",
  "models": ["FM1"]
}
```

**Expected Output** (`tests/corpus/expected/invalid-schema-missing-field.errs.json`):
```json
["ERR-SCHEMA-001"]
```

**Mirror Implementation Must:**
- Detect missing required field (`instance`)
- Return schema validation error
- Match error code exactly

---

### Example 3: FM30 Dominance

**Input** (`tests/corpus/invalid/invalid-governance-unrecoverable.json`):
```json
{
  "id": "unrecoverable-test",
  "domain": "core",
  "class": "99",
  "instance": "test",
  "models": ["FM30"]
}
```

**Expected Output** (`tests/corpus/expected/invalid-governance-unrecoverable.errs.json`):
```json
["ERR-FM30-001"]
```

**Mirror Implementation Must:**
- Implement FM30 dominance rule correctly
- Suppress non-FM30 errors when FM30 present
- Return only FM30-tagged errors

---

## Troubleshooting

### Issue: False Positives on Valid Corpus

**Symptoms:** Valid artifacts produce errors

**Causes:**
- Schema validation too strict
- Missing schema rules
- Incorrect required field list

**Fix:**
1. Compare schema against canonical `schemas/v1.0.0/artifact.schema.json`
2. Verify all required vs optional fields
3. Check JSON Schema validation logic

---

### Issue: Wrong Error Codes

**Symptoms:** Error codes differ from expected

**Causes:**
- Incorrect FM mapping
- Wrong error registry
- FM30 dominance not implemented

**Fix:**
1. Verify `registries/mappings.json` copied correctly
2. Verify `registries/err.json` copied correctly
3. Implement FM30 dominance rule (see `base120/validators/errors.py`)

---

### Issue: Non-Deterministic Output

**Symptoms:** Different output across runs

**Causes:**
- Timestamps in error output
- Random ordering (unsorted errors)
- Environment-dependent behavior

**Fix:**
1. Respect `BASE120_FIXED_TIMESTAMP` environment variable
2. Sort error arrays lexicographically before returning
3. Remove any random/non-deterministic logic

---

### Issue: Extra or Missing Errors

**Symptoms:** Error count doesn't match expected

**Causes:**
- Missing validation stage
- Extra validation logic not in canonical
- Incorrect error deduplication

**Fix:**
1. Follow canonical validation pipeline exactly:
   - Schema validation → early return on failure
   - Subclass → FM mapping
   - FM → Error resolution
2. Deduplicate errors before sorting
3. Don't add extra validation beyond canonical

---

## Reference Materials

### Canonical Implementation

- **Repository**: https://github.com/hummbl-dev/base120
- **Validator Entry Point**: `base120/validators/validate.py::validate_artifact()`
- **Validation Pipeline**: `base120/validators/` (schema.py, mappings.py, errors.py)
- **Golden Corpus**: `tests/corpus/`
- **Registries**: `registries/` (mappings.json, fm.json, err.json)

### Key Documents

- **Governance**: `GOVERNANCE.md` - Change taxonomy and invariants
- **Corpus Contract**: `docs/corpus-contract.md` - Golden corpus definition
- **Specification**: `docs/spec-v1.0.0.md` - Formal specification (if available)
- **Mirror README**: `mirrors/README.md` - Official mirror registry

### Validation Pipeline Order

```
1. Schema Validation (schema.py)
   ├─ Pass → Continue
   └─ Fail → Return ["ERR-SCHEMA-001"]

2. FM Mapping (mappings.py)
   └─ artifact.class → FM set (from registries/mappings.json)

3. Error Resolution (errors.py)
   ├─ FM set → Error codes (from registries/err.json)
   ├─ Apply FM30 dominance rule
   ├─ Deduplicate errors
   └─ Sort lexicographically
```

---

## Contact & Support

**Mirror Conformance Issues:**
- Open issue in `hummbl-dev/base120` with label `mirror-conformance`
- Include CI logs, diff output, and reproduction steps

**Certification Requests:**
- Open issue with label `mirror-certification`
- Include all prerequisites from [Certification Process](#certification-process)

**Governance Escalation:**
- For conformance contract changes, open issue with label `governance`
- Tag `@hummbl-dev` for review

---

## Conformance Contract Versioning

**Current Version**: 1.0.0  
**Effective Date**: 2026-01-04  
**Status**: Enforcement-Grade  

**Change History:**
- v1.0.0 (2026-01-04): Initial conformance contract with lifecycle states and CI enforcement

**Compatibility:**
- Applies to Base120 v1.0.x canonical implementation
- Mirror implementations targeting v1.0.x MUST conform to this contract

---

**Document Authority**: This contract is the authoritative specification for mirror conformance.  
**Enforcement**: CI-automated via `.github/workflows/mirror-conformance.yml`  
**Governance**: Changes require approval per `GOVERNANCE.md` (Level 4: Schema/Contract changes)
