# Base120 Governance System

This directory contains the automated governance enforcement system for the Base120 repository.

## Overview

Base120 implements a **proscriptive governance contract** that is automatically enforced by CI workflows. This ensures:

- **Deterministic validation** across all implementations
- **Mathematical rigor** in formal model changes
- **Audit trails** for all substantive changes
- **Version policy enforcement** (v1.0.x frozen specification)

## Documentation

### For Contributors

1. **[Governance Decision Tree](../../docs/governance-decision-tree.md)**
   - Quick reference for classifying your changes
   - Flowchart-style decision support
   - Checklists for each change class

2. **[Migration Guide](../../docs/governance-migration.md)**
   - Adapting to governance v2.0.0
   - Common scenarios and examples
   - Troubleshooting CI failures

3. **[GOVERNANCE.md](../../GOVERNANCE.md)**
   - Complete governance specification
   - Change taxonomy (6 classes)
   - Invariants and enforcement rules
   - Evidence requirements matrix

### For Maintainers

- **Workflow Architecture** (see below)
- **Custom Workflow Development** (see Extending section)
- **Override Procedures** (see GOVERNANCE.md)

---

## Workflow Architecture

### governance-classifier.yml

**Purpose:** Automatically detect change class and requirements

**Triggers:**
- Pull request opened/synchronized/reopened
- Manual dispatch

**Outputs:**
- Change class (trivial/editorial/corpus/schema/fm/breaking)
- Impact level (1-5)
- Required reviewers
- Evidence checklist

**Posts to PR:**
- Classification comment with requirements
- Updates automatically on push

---

### governance-invariants.yml

**Purpose:** Enforce core Base120 invariants

**Triggers:**
- Pull request to main
- Push to main
- Manual dispatch

**Checks:**
1. **Golden Corpus Determinism**
   - Runs corpus tests 3 times
   - Hashes outputs, verifies byte-for-byte identity
   - Fails if any non-determinism detected

2. **Backward Compatibility**
   - Runs all valid corpus tests
   - Ensures all pass (empty error list)
   - Fails if any valid artifact now fails

3. **Registry Integrity**
   - Validates FM references are well-formed
   - Checks for orphaned FMs
   - Verifies no duplicate IDs
   - Blocks unauthorized v1.0.x registry changes

4. **FM30 Dominance**
   - Tests FM30 dominance rule
   - Ensures only FM30-tagged errors when FM30 present

5. **Schema Validation**
   - Self-validates artifact schema
   - Ensures schema is valid JSON Schema

---

### governance-audit.yml

**Purpose:** Verify audit trail requirements

**Triggers:**
- Pull request to main
- Manual dispatch

**Checks:**
1. **Change Class Detection**
   - Determines if audit is required
   - Based on file patterns

2. **Audit Update Verification**
   - Checks for GOVERNANCE.md or CHANGELOG updates
   - Warning if missing (will become hard failure in Phase 2)

3. **Commit Message Quality**
   - Checks for issue references
   - Warns if traceability missing

4. **PR Description**
   - Checks for impact analysis keywords
   - Warns if justification appears missing

**Current Status:** Soft warnings (Phase 1)

---

### governance-version.yml

**Purpose:** Enforce v1.0.x frozen specification policy

**Triggers:**
- Pull request to main
- Manual dispatch

**v1.0.x Enforcement:**
- ✅ Permits: Security fixes, CI hardening, documentation, corpus additions
- ❌ Blocks: Schema changes, registry changes, semantic validator changes, breaking changes

**Hard Failures:**
- Schema modifications in v1.0.x
- Registry modifications in v1.0.x

**Soft Warnings:**
- Validator logic changes (requires justification)
- Corpus modifications (requires extra review)

---

### mirror-conformance.yml

**Purpose:** Reusable workflow for validating mirror implementations

**Type:** Reusable workflow (not triggered directly in canonical repo)

**Usage:** Called by mirror repositories via `workflow_call`

**Inputs:**
- `language`: Programming language of the mirror
- `validate-command`: Command to run validator CLI
- `setup-command`: Setup steps (install, build, etc.)
- `corpus-path`: Path to corpus directory (default: tests/corpus)

**Validates:**
1. **Golden Corpus Conformance**
   - Clones canonical corpus from hummbl-dev/base120
   - Runs mirror validator against all test cases
   - Compares outputs byte-for-byte

2. **Determinism**
   - Runs validator 3 times on sample artifacts
   - Verifies outputs are identical across runs

3. **Error Matching**
   - Valid corpus → Must return `[]`
   - Invalid corpus → Must match expected errors exactly

**Outputs:**
- Detailed pass/fail report in workflow logs
- PR comment with results and failure details
- Blocks merge if any conformance failures

**Documentation:**
- **[mirrors/CONFORMANCE_CONTRACT.md](../../mirrors/CONFORMANCE_CONTRACT.md)** - Full conformance requirements
- **[mirrors/README.md](../../mirrors/README.md)** - Mirror certification process

---

## Enforcement Phases

### Phase 1: Soft Enforcement (Current)

**Duration:** 2-4 weeks

**Characteristics:**
- All workflows active
- Most checks are warnings, not hard failures
- Education and feedback period
- Contributors can learn the system

**Hard Failures:**
- Schema/registry changes in v1.0.x
- Corpus determinism violations
- Test failures

---

### Phase 2: Gradual Hardening (Future)

**Duration:** 2-4 weeks

**Characteristics:**
- Audit checks become hard failures
- Version policy strictly enforced
- Change classifier suggestions become requirements
- Grace period for existing PRs

**New Hard Failures:**
- Missing audit updates (Level 3+)
- Insufficient reviewers
- Missing evidence artifacts

---

### Phase 3: Full Enforcement (Future)

**Duration:** Ongoing

**Characteristics:**
- All checks are hard failures
- No overrides except security/emergency
- Governance contract fully automated
- System scales to team without modification

---

## Local Testing

Before pushing, you can test governance compliance locally:

### Test 1: Classify Your Changes

```bash
# See what files changed
git diff --name-only main

# Match against patterns:
# - Only *.md → Trivial/Editorial
# - tests/corpus/ → Corpus
# - schemas/ → Schema
# - registries/ → FM
```

### Test 2: Run Corpus Tests

```bash
# Required for Level 3+
pytest tests/test_corpus.py -v

# Should pass with no failures
```

### Test 3: Run Full Test Suite

```bash
# Required for Level 4+
pytest -v

# All 40 tests should pass
```

### Test 4: Check Determinism

```bash
# Run corpus tests 3 times, compare outputs
for i in 1 2 3; do
  pytest tests/test_corpus.py --tb=short 2>&1 | sha256sum
done

# All hashes should be identical
```

### Test 5: Validate Registries

```bash
# Check registry integrity
python3 << 'PYTHON'
import json
with open("registries/fm.json") as f:
    fm_reg = json.load(f)
with open("registries/mappings.json") as f:
    map_reg = json.load(f)
with open("registries/err.json") as f:
    err_reg = json.load(f)

fm_ids = {fm["id"] for fm in fm_reg["registry"]}
print(f"Found {len(fm_ids)} FMs")

# Check mappings reference valid FMs
for subclass, fms in map_reg["mappings"].items():
    for fm in fms:
        assert fm in fm_ids, f"Unknown FM: {fm}"
print("✅ Mappings valid")

# Check errors reference valid FMs
for err in err_reg["registry"]:
    for fm in err["fm"]:
        assert fm in fm_ids, f"Unknown FM: {fm}"
print("✅ Errors valid")
PYTHON
```

### Test 6: Check Version Policy

```bash
# Check current version
grep '^version' pyproject.toml

# Check for prohibited changes (if v1.0.x)
git diff --name-only main | grep -E 'schemas/v1.0.0/|registries/'
# No output → OK
# Any output → PROHIBITED in v1.0.x
```

---

## Extending the System

### Adding a New Workflow

1. Create `.github/workflows/governance-{name}.yml`
2. Follow existing workflow patterns
3. Use clear error messages
4. Document in this README
5. Test locally first
6. Submit as Level 4+ change

### Adding a New Invariant

1. Define invariant in GOVERNANCE.md
2. Add test to `governance-invariants.yml`
3. Provide clear failure messages
4. Submit as Level 5 change (requires proof)

### Modifying Classification Logic

1. Update patterns in `governance-classifier.yml`
2. Test on diverse file sets
3. Document in governance-decision-tree.md
4. Submit as Level 4+ change

---

## Troubleshooting

### Workflow Not Running

**Check:**
- Is PR targeting `main` branch?
- Are file paths in trigger conditions correct?
- Check GitHub Actions tab for execution logs

### False Positive Classification

**Action:**
1. Add comment to PR explaining why classification is incorrect
2. Provide justification
3. Request CODEOWNER override
4. Document in PR description

### Audit Check Failing

**Fix:**
```bash
# Add audit entry
vim GOVERNANCE.md
# Or
vim CHANGELOG

# Commit
git add GOVERNANCE.md
git commit -m "Add audit trail for [change]"
git push
```

### Version Policy Blocking Valid Change

**Options:**
1. Verify change is truly permitted in v1.0.x
2. Add justification to PR description
3. Request governance override
4. Defer to v1.1.0 if truly prohibited

---

## Metrics & Observability

### Success Metrics

- **Classification Accuracy:** 95%+ correct auto-classification
- **False Positive Rate:** <5% incorrect blocks
- **Mean Time to Merge:** <24h for Level 1-2, <72h for Level 3-5
- **Governance Violations:** Zero post-merge violations

### Monitoring

- Check GitHub Actions tab regularly
- Review failed checks for patterns
- Collect feedback from contributors
- Iterate on classification logic

### Feedback Loop

1. Contributor hits false positive
2. Documents scenario in issue
3. Governance team reviews
4. Updates classification logic or documentation
5. Deploys improved workflow

---

## Security Considerations

### Override Authority

Only CODEOWNER can:
- Override governance checks (emergency)
- Approve security exception PRs
- Merge with governance violations

### Audit Trail

All overrides must be documented within 7 days in GOVERNANCE.md

### Escalation

Security vulnerabilities bypass normal review requirements but require post-merge audit

---

## Related Documentation

- **[GOVERNANCE.md](../../GOVERNANCE.md)** - Complete governance specification
- **[governance-decision-tree.md](../../docs/governance-decision-tree.md)** - Classification quick reference
- **[governance-migration.md](../../docs/governance-migration.md)** - Migration from v1.0.0
- **[corpus-contract.md](../../docs/corpus-contract.md)** - Golden corpus specification
- **[mirrors/CONFORMANCE_CONTRACT.md](../../mirrors/CONFORMANCE_CONTRACT.md)** - Mirror conformance contract
- **[mirrors/README.md](../../mirrors/README.md)** - Mirror certification and registry

---

## Changelog

### 2026-01-04: Mirror Conformance Infrastructure
- Added mirror-conformance.yml reusable workflow
- Created mirrors/CONFORMANCE_CONTRACT.md
- Created mirrors/README.md with certification process
- Documented mirror lifecycle states
- Enabled automated conformance validation for mirror repos

### 2026-01-03: v2.0.0 Initial Release
- Formalized governance contract
- Implemented 4 enforcement workflows
- Created comprehensive documentation
- Established 3-phase rollout plan

---

## Contact

**Governance Questions:** Create issue with `governance` label  
**Override Requests:** Tag @hummbl-dev with `governance-override` label  
**Bug Reports:** Create issue with workflow logs attached  
**Feedback:** Comment on issue #19

---

**Status:** Phase 1 (Soft Enforcement)  
**Document Version:** 1.0.0  
**Last Updated:** 2026-01-03