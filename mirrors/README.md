# Base120 Mirror Implementations

This directory tracks official mirror implementations of Base120 in other programming languages. All mirrors MUST conform to the [Conformance Contract](CONFORMANCE_CONTRACT.md).

---

## Official Mirrors

### Status Legend

- 🟢 **Approved**: Certified conformant, production-ready
- 🟡 **Review**: Under evaluation, validation in progress
- 🔴 **Draft**: Work in progress, not yet validated
- ⚫ **Deprecated**: No longer maintained, use alternatives

### Certified Mirrors

Currently, there are no certified mirror implementations. The Python implementation at `hummbl-dev/base120` is the canonical reference.

**Want to create a mirror?** See [Creating a Mirror](#creating-a-mirror) below.

---

## Mirror Requirements

All mirror implementations MUST:

1. **Golden Corpus Conformance**
   - Pass 100% of golden corpus tests
   - Produce byte-for-byte identical outputs to canonical implementation
   - Validate deterministically (same input → same output, every time)

2. **CI Integration**
   - Integrate the [reusable conformance workflow](#ci-integration)
   - Run conformance checks on every PR
   - Block merges on conformance failures

3. **Documentation**
   - README with installation and usage instructions
   - API documentation matching canonical semantics
   - Examples demonstrating typical usage

4. **Licensing**
   - MIT, Apache 2.0, or compatible open source license
   - No proprietary restrictions

5. **Maintenance**
   - Respond to conformance failures within 7 days
   - Update when canonical corpus changes
   - Maintain backward compatibility within v1.0.x

See the [Conformance Contract](CONFORMANCE_CONTRACT.md) for detailed requirements.

---

## Creating a Mirror

### Step 1: Understand the Canonical Implementation

1. Clone the canonical repository:
   ```bash
   git clone https://github.com/hummbl-dev/base120.git
   cd base120
   ```

2. Study the validation pipeline:
   - **Entry Point**: `base120/validators/validate.py::validate_artifact()`
   - **Pipeline Order**:
     1. Schema validation (`base120/validators/schema.py`)
     2. FM mapping (`base120/validators/mappings.py`)
     3. Error resolution (`base120/validators/errors.py`)

3. Review key resources:
   - **Schema**: `schemas/v1.0.0/artifact.schema.json`
   - **Registries**: `registries/` (mappings.json, fm.json, err.json)
   - **Golden Corpus**: `tests/corpus/`
   - **Governance**: `GOVERNANCE.md`

4. Run the tests to understand expected behavior:
   ```bash
   pip install -e ".[test]"
   pytest tests/test_corpus.py -v
   ```

### Step 2: Implement Core Validation

1. **Create validator function**:
   - Input: Artifact JSON object
   - Output: Array of error code strings (sorted lexicographically)
   - Return `[]` for valid artifacts

2. **Implement validation pipeline**:
   ```
   1. Schema Validation
      ├─ Pass → Continue to step 2
      └─ Fail → Return ["ERR-SCHEMA-001"]
   
   2. FM Mapping
      └─ artifact.class → FM set (from registries/mappings.json)
   
   3. Error Resolution
      ├─ FM set → Error codes (from registries/err.json)
      ├─ Apply FM30 dominance rule
      ├─ Deduplicate errors
      └─ Sort lexicographically
   ```

3. **Key implementation notes**:
   - **Schema-first**: Schema failures short-circuit (no further validation)
   - **FM30 dominance**: When FM30 present, suppress non-FM30 errors
   - **Determinism**: No timestamps, randomness, or environment-dependent logic
   - **Canonical JSON**: Sorted keys, UTF-8, no extra whitespace

### Step 3: Copy Canonical Resources

Copy these files to your mirror repository:

```bash
# Schemas
cp -r schemas/ /path/to/your/mirror/schemas/

# Registries
cp -r registries/ /path/to/your/mirror/registries/

# Golden Corpus
cp -r tests/corpus/ /path/to/your/mirror/tests/corpus/
```

**Important**: These files are read-only. Do not modify them. They define the contract.

### Step 4: Create CLI Validator

Create a CLI that:
- Accepts artifact JSON file path as argument
- Outputs error array JSON to stdout
- Respects `BASE120_FIXED_TIMESTAMP` environment variable (for deterministic testing)

Example:

```bash
$ your-validator tests/corpus/valid/valid-basic.json
[]

$ your-validator tests/corpus/invalid/invalid-schema-missing-field.json
["ERR-SCHEMA-001"]
```

### Step 5: Integrate CI Workflow

Create `.github/workflows/conformance.yml`:

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
      language: 'javascript'  # Change to your language
      validate-command: 'node dist/validate.js'  # Change to your CLI command
      setup-command: 'npm install && npm run build'  # Change to your setup
      corpus-path: 'tests/corpus'  # Optional: change if different path
```

**Workflow inputs**:
- `language`: Your implementation language (e.g., 'javascript', 'go', 'rust')
- `validate-command`: Command to run your validator (receives artifact path as arg)
- `setup-command`: Setup steps (install deps, build, etc.)
- `corpus-path`: Path to corpus directory (default: 'tests/corpus')

### Step 6: Test Locally

Before pushing, validate locally:

```bash
# Run your validator against all valid corpus
for file in tests/corpus/valid/*.json; do
  output=$(your-validator "$file")
  if [ "$output" != "[]" ]; then
    echo "FAIL: $file produced $output"
  fi
done

# Run your validator against all invalid corpus
for file in tests/corpus/invalid/*.json; do
  expected=$(cat "tests/corpus/expected/$(basename "$file" .json).errs.json")
  output=$(your-validator "$file")
  if [ "$output" != "$expected" ]; then
    echo "FAIL: $file"
    echo "  Expected: $expected"
    echo "  Got: $output"
  fi
done
```

### Step 7: Request Certification

Once your mirror passes all tests:

1. Open an issue in `hummbl-dev/base120`:
   - Title: `[Mirror Certification] <Language> Implementation`
   - Include:
     - Link to your repository
     - CI workflow status badge
     - Conformance test results
     - Usage documentation

2. External reviewer will:
   - Validate conformance
   - Review documentation
   - Confirm deterministic behavior

3. Upon approval:
   - Mirror added to this README as **Approved**
   - Announcement in canonical repository
   - Recognition in Base120 ecosystem

---

## CI Integration

### Reusable Workflow

The canonical repository provides a reusable GitHub Actions workflow at:

```
hummbl-dev/base120/.github/workflows/mirror-conformance.yml@main
```

This workflow:
- Clones canonical corpus
- Runs your validator against all test cases
- Compares outputs byte-for-byte
- Verifies determinism
- Posts detailed PR comments
- Blocks merge on conformance failures

### Usage Example

```yaml
name: Mirror Conformance

on:
  pull_request:
  push:
    branches: [main]

jobs:
  conformance:
    uses: hummbl-dev/base120/.github/workflows/mirror-conformance.yml@main
    with:
      language: 'typescript'
      validate-command: 'npm run validate'
      setup-command: 'npm ci && npm run build'
```

### Workflow Outputs

**On Success** (100% conformance):
```
✅ CONFORMANCE CHECK PASSED

Valid Corpus:   4/4 passed
Invalid Corpus: 3/3 passed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall:        7/7 passed (100%)

✅ Determinism: PASSED
```

**On Failure** (any test fails):
```
❌ CONFORMANCE CHECK FAILED

Valid Corpus:   3/4 passed (75.0%)
Invalid Corpus: 2/3 passed (66.7%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall:        5/7 passed (71.4%)

❌ Failures:
  - valid-example-4.json: Expected [], got ["ERR-SCHEMA-001"]
  - invalid-recovery-plus-unrecoverable.json: Expected ["ERR-FM30-001"], got ["ERR-FM30-001", "ERR-FM15-001"]
```

### Local Testing

Test the workflow locally before pushing:

```bash
# Install act (GitHub Actions local runner)
# https://github.com/nektos/act

# Run conformance workflow
act pull_request -W .github/workflows/conformance.yml
```

---

## Certification Process

### Overview

Mirror certification verifies that an implementation produces byte-for-byte identical outputs to the canonical validator for all golden corpus test cases.

### States

1. **Draft** → Implementation in progress
2. **Review** → Validation underway, CI integrated
3. **Approved** → Certified conformant, production-ready
4. **Deprecated** → No longer maintained
5. **Removed** → Delisted from registry

See [Conformance Contract: Mirror Lifecycle States](CONFORMANCE_CONTRACT.md#mirror-lifecycle-states) for detailed state definitions.

### Requirements

- ✅ 100% golden corpus conformance
- ✅ CI workflow integrated
- ✅ Documentation complete
- ✅ At least 1 external review
- ✅ Compatible license (MIT, Apache 2.0, etc.)

### Timeline

- **Review Period**: 1-4 weeks (depending on reviewer availability)
- **Re-certification**: Required after major version updates or corpus changes

### Maintaining Certification

Approved mirrors MUST:
- Run conformance CI on every PR
- Respond to conformance failures within 7 days
- Update when canonical corpus changes
- Maintain public issue tracker

---

## Troubleshooting

### Common Issues

**Issue**: Validator produces wrong error codes

**Solution**:
1. Verify registries copied correctly from canonical repo
2. Check FM mapping logic (subclass → FM set)
3. Verify error resolution logic (FM set → error codes)
4. Ensure FM30 dominance rule implemented

---

**Issue**: Non-deterministic output

**Solution**:
1. Remove timestamps from error output
2. Sort error arrays lexicographically before returning
3. Respect `BASE120_FIXED_TIMESTAMP` environment variable
4. Check for random/environment-dependent logic

---

**Issue**: Valid artifacts produce errors (false positives)

**Solution**:
1. Compare schema against canonical `schemas/v1.0.0/artifact.schema.json`
2. Verify required vs optional fields
3. Check JSON Schema validation implementation

---

**Issue**: Invalid artifacts pass validation (false negatives)

**Solution**:
1. Ensure schema validation runs first
2. Verify schema validation failures return `["ERR-SCHEMA-001"]` immediately
3. Check FM mapping and error resolution logic

---

See [Conformance Contract: Troubleshooting](CONFORMANCE_CONTRACT.md#troubleshooting) for more detailed guidance.

---

## Resources

### Documentation

- **[Conformance Contract](CONFORMANCE_CONTRACT.md)** - Detailed conformance requirements
- **[Governance](../GOVERNANCE.md)** - Change management and invariants
- **[Corpus Contract](../docs/corpus-contract.md)** - Golden corpus definition
- **[Specification](../docs/spec-v1.0.0.md)** - Formal specification (if available)

### Canonical Implementation

- **Repository**: https://github.com/hummbl-dev/base120
- **Validator**: `base120/validators/validate.py::validate_artifact()`
- **Tests**: `tests/test_corpus.py`
- **Schemas**: `schemas/v1.0.0/artifact.schema.json`
- **Registries**: `registries/` (mappings.json, fm.json, err.json)

### Getting Help

- **Questions**: Open a discussion in `hummbl-dev/base120`
- **Issues**: Open an issue with label `mirror-conformance`
- **Certification**: Open an issue with label `mirror-certification`

---

## Contributing

Mirror implementations are community-driven. Contributions welcome!

**How to contribute:**
1. Create a mirror implementation (see [Creating a Mirror](#creating-a-mirror))
2. Achieve 100% golden corpus conformance
3. Integrate CI workflow
4. Request certification
5. Maintain conformance over time

**Recognition:**
- Approved mirrors listed in this README
- Credit in Base120 ecosystem
- Community support and visibility

---

**Last Updated**: 2026-01-04  
**Document Version**: 1.0.0  
**Status**: Official Mirror Registry

**Maintenance Note**: This document should be updated when:
- New mirrors are certified or deprecated
- Conformance requirements change
- CI workflow inputs or behavior changes
- Troubleshooting guidance is added or updated
