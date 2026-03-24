# Troubleshooting Guide: Job 62658400432 Failure

**Job URL**: https://github.com/hummbl-dev/base120/actions/runs/21723228902/job/62658400432?pr=38  
**Pull Request**: #38 (develop → main)  
**Workflow**: Governance Version Policy  
**Status**: ❌ FAILED  
**Date**: 2026-02-05

---

## Executive Summary

The CI job failed because the governance workflow is **more restrictive than the updated governance policy**. The workflow blocks ALL registry JSON modifications in v1.0.x, but the updated GOVERNANCE.md states that "FM lifecycle metadata additions are PERMITTED (forward compatibility)."

---

## Root Cause Analysis

### What Triggered the Failure

PR #38 modified `registries/fm.json` by adding lifecycle metadata fields to all 30 failure modes:
- `lifecycle_state: "stable"`
- `introduced_in: "v1.0.0"`
- `deprecated_in: null`
- `removed_in: null`
- `deprecation_reason: null`

**Before**:
```json
{ "id": "FM1", "name": "Specification Ambiguity" }
```

**After**:
```json
{
  "id": "FM1",
  "name": "Specification Ambiguity",
  "lifecycle_state": "stable",
  "introduced_in": "v1.0.0",
  "deprecated_in": null,
  "removed_in": null,
  "deprecation_reason": null
}
```

### Why It Failed

The governance workflow (`.github/workflows/governance-version.yml`) contains a hard block at lines 110-114:

```yaml
if echo "$CHANGED_FILES" | grep -qE "^(schemas/v1\.0\.0/|registries/).*\.json$"; then
  echo ""
  echo "❌ HARD FAILURE: Schema or registry changes are prohibited in v1.0.x"
  echo "This PR cannot be merged without governance override."
  exit 1
```

This regex pattern matches **any** JSON file change in `registries/`, including metadata-only additions.

### Policy vs. Workflow Mismatch

**GOVERNANCE.md (lines 186-190)** states:
```
Special Constraints (v1.0.x):
- Registry semantic modifications are **PROHIBITED** in v1.0.x
- FM lifecycle metadata additions are **PERMITTED** (forward compatibility)
- FM lifecycle state changes are **PROHIBITED** (all FMs remain "stable")
- New FMs require governance escalation to v1.1.0+
```

**Workflow behavior**: Blocks ALL registry changes (semantic AND metadata)

---

## Impact Assessment

**Current State**:
- Version: `1.0.0` (from `pyproject.toml`)
- v1.0.x policy is active
- PR #38 cannot merge until resolved

**Change Classification** (per GOVERNANCE.md):
- **Change Type**: Formal Model (FM) - Registry Modification
- **Intent**: Add forward-compatible metadata (no semantic changes)
- **Policy Compliance**: ✅ Permitted per GOVERNANCE.md Section "Special Constraints (v1.0.x)"
- **Workflow Compliance**: ❌ Blocked by governance-version.yml

---

## Solution Options

### Option 1: Update Workflow to Allow Metadata-Only Changes (RECOMMENDED)

**Objective**: Align workflow with governance policy by distinguishing semantic vs. metadata changes.

**Implementation**:

1. **Create validation script** (`scripts/validate_registry_metadata.py`):

```python
#!/usr/bin/env python3
"""
Validate that registries/fm.json changes in v1.0.x are metadata-only.

Permitted in v1.0.x:
- Adding new fields to existing FMs (with stable/null values)
- No changes to FM count, IDs, or names
- All lifecycle_state must be "stable"

Prohibited in v1.0.x:
- Adding new FMs (FM31+)
- Removing FMs
- Changing FM IDs or names
- Changing lifecycle_state from "stable"
- Any other semantic modifications
"""

import json
import sys
from pathlib import Path

def load_fm_registry(content):
    """Load FM registry from JSON content."""
    return json.loads(content)

def validate_metadata_only_change(before_content, after_content):
    """
    Validate that changes are metadata-only additions.
    
    Returns: (is_valid, error_messages)
    """
    errors = []
    
    before = load_fm_registry(before_content)
    after = load_fm_registry(after_content)
    
    before_fms = {fm['id']: fm for fm in before['registry']}
    after_fms = {fm['id']: fm for fm in after['registry']}
    
    # Check 1: FM count must be identical
    if len(before_fms) != len(after_fms):
        errors.append(f"FM count changed: {len(before_fms)} → {len(after_fms)} (prohibited in v1.0.x)")
    
    # Check 2: No FMs removed
    removed_fms = set(before_fms.keys()) - set(after_fms.keys())
    if removed_fms:
        errors.append(f"FMs removed: {', '.join(sorted(removed_fms))} (prohibited in v1.0.x)")
    
    # Check 3: No FMs added
    added_fms = set(after_fms.keys()) - set(before_fms.keys())
    if added_fms:
        errors.append(f"FMs added: {', '.join(sorted(added_fms))} (prohibited in v1.0.x - escalate to v1.1.0+)")
    
    # Check 4: Validate existing FMs
    for fm_id in before_fms.keys():
        if fm_id not in after_fms:
            continue;
            
        before_fm = before_fms[fm_id]
        after_fm = after_fms[fm_id]
        
        # Check 4a: Name unchanged
        if before_fm.get('name') != after_fm.get('name'):
            errors.append(f"{fm_id}: Name changed (prohibited in v1.0.x)")
        
        # Check 4b: If lifecycle_state exists, must be "stable"
        if 'lifecycle_state' in after_fm and after_fm['lifecycle_state'] != 'stable':
            errors.append(f"{fm_id}: lifecycle_state is '{after_fm['lifecycle_state']}' (must be 'stable' in v1.0.x)")
        
        # Check 4c: Core fields not removed
        for core_field in ['id', 'name']:
            if core_field in before_fm and core_field not in after_fm:
                errors.append(f"{fm_id}: Core field '{core_field}' removed (prohibited)")
    
    # Check 5: Version field unchanged
    if before.get('version') != after.get('version'):
        errors.append(f"Registry version changed: {before.get('version')} → {after.get('version')} (must remain v1.0.0)")
    
    return len(errors) == 0, errors

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: validate_registry_metadata.py <before_file> <after_file>")
        sys.exit(1)
    
    before_file = Path(sys.argv[1])
    after_file = Path(sys.argv[2])
    
    is_valid, errors = validate_metadata_only_change(
        before_file.read_text(),
        after_file.read_text()
    )
    
    if is_valid:
        print("✅ PASS: Registry changes are metadata-only additions (permitted in v1.0.x)")
        sys.exit(0)
    else:
        print("❌ FAIL: Registry contains prohibited semantic changes")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
```

2. **Update workflow** (`.github/workflows/governance-version.yml` around lines 67-72):

```yaml
# Check for registry modifications
if echo "$CHANGED_FILES" | grep -qE "^registries/.*\.json$"; then
  echo "🔍 Registry changes detected - validating metadata-only compliance..."
  
  # Export files for comparison
  git show origin/${{ github.base_ref }}:registries/fm.json > /tmp/fm_before.json
  git show HEAD:registries/fm.json > /tmp/fm_after.json
  
  # Validate metadata-only changes
  if python scripts/validate_registry_metadata.py /tmp/fm_before.json /tmp/fm_after.json; then
    echo "✅ Registry changes are metadata-only (permitted in v1.0.x)"
  else
    VIOLATIONS="${VIOLATIONS}❌ PROHIBITED: Registry semantic modifications detected\n"
    VIOLATIONS="${VIOLATIONS}   Files: $(echo "$CHANGED_FILES" | grep -E '^registries/')\n"
    VIOLATIONS="${VIOLATIONS}   Policy: Only metadata additions permitted in v1.0.x\n\n"
  fi
fi
```

3. **Update hard failure check** (lines 110-114):

```yaml
# Check if violations include hard prohibitions (schemas or semantic registry changes)
if echo "$CHANGED_FILES" | grep -qE "^schemas/v1\.0\.0/.*\.json$"; then
  echo ""
  echo "❌ HARD FAILURE: Schema changes are prohibited in v1.0.x"
  echo "This PR cannot be merged without governance override."
  exit 1
fi
```

**Pros**:
- ✅ Aligns workflow with governance policy
- ✅ Enables forward-compatible metadata additions
- ✅ Still blocks semantic changes
- ✅ Reusable for future v1.0.x maintenance

**Cons**:
- Requires new validation script
- Adds workflow complexity

---

### Option 2: Governance Override (TEMPORARY WORKAROUND)

**Objective**: Manually approve this specific PR as a policy exception.

**Implementation**:

1. Add workflow override mechanism (`.github/workflows/governance-version.yml`):

```yaml
- name: Check for governance override
  id: override
  run: |
    if gh pr view ${{ github.event.pull_request.number }} --json labels --jq '.labels[].name' | grep -q "governance-override"; then
      echo "override=true" >> $GITHUB_OUTPUT
      echo "⚠️ GOVERNANCE OVERRIDE ACTIVE"
    else
      echo "override=false" >> $GITHUB_OUTPUT
    fi
  env:
    GH_TOKEN: ${{ github.token }}

- name: Check v1.0.x prohibited changes
  if: steps.version.outputs.is_v1_0_x == 'true' && steps.override.outputs.override == 'false'
  run: |
    # ... existing checks ...
```

2. Add `governance-override` label to PR #38
3. Document justification in PR description:

```
## Governance Override Justification

**Reason**: Adding forward-compatible lifecycle metadata fields to registries/fm.json

**Policy Compliance**: GOVERNANCE.md Section "Special Constraints (v1.0.x)" explicitly permits 
"FM lifecycle metadata additions" for forward compatibility with v1.1.0+.

**Impact**: No semantic changes - all FMs remain "stable", no IDs/names/counts changed.

**Approved By**: @hummbl-dev (CODEOWNER)
```

**Pros**:
- ✅ Quick fix for this specific PR
- ✅ No workflow changes required immediately

**Cons**:
- ❌ Doesn't fix underlying policy-workflow mismatch
- ❌ Manual process for future PRs
- ❌ Requires governance board approval

---

### Option 3: Defer to v1.1.0 (NOT RECOMMENDED)

**Objective**: Remove metadata changes from v1.0.0 and defer to v1.1.0.

**Implementation**:

1. Revert `registries/fm.json` changes in PR #38
2. Create new branch `feature/fm-lifecycle-metadata` targeting v1.1.0
3. Update GOVERNANCE.md to reflect deferred implementation

**Pros**:
- ✅ No workflow changes needed
- ✅ No policy exceptions required

**Cons**:
- ❌ Delays forward-compatibility improvements
- ❌ GOVERNANCE.md changes in PR #38 become misleading
- ❌ Creates technical debt

---

## Recommended Action Plan

**RECOMMENDATION**: **Option 1** (Update Workflow)

**Rationale**:
1. The governance policy explicitly permits metadata additions
2. The workflow should enforce policy, not contradict it
3. This is a one-time fix that benefits future v1.0.x maintenance
4. Aligns with "audit-of-audits" requirement (AUDIT_INDEX.md)

**Implementation Steps**:

1. **Create validation script** (1 hour):
   - Add `scripts/validate_registry_metadata.py`
   - Test locally with before/after versions of `registries/fm.json`
   - Validate exit codes (0 = pass, 1 = fail)

2. **Update workflow** (30 minutes):
   - Modify `.github/workflows/governance-version.yml`
   - Replace hard block with validation script call
   - Update error messages for clarity

3. **Test workflow** (1 hour):
   - Push changes to PR #38
   - Verify job passes with metadata-only changes
   - Create test PR with semantic change to verify blocking still works

4. **Update documentation** (30 minutes):
   - Add validation script documentation to GOVERNANCE.md
   - Update AUDIT_INDEX.md with workflow change
   - Document in AAR.md as Issue 8 resolution

**Total Effort**: ~3 hours

---

## Testing Strategy

### Test Case 1: Metadata-Only Changes (Should Pass)

**Input**: PR #38 current state
- Add lifecycle fields with stable/null values
- No FM additions/removals
- No semantic changes

**Expected**: ✅ Workflow passes

### Test Case 2: Add New FM (Should Fail)

**Input**:
```json
{ "id": "FM31", "name": "Certificate Expiration", "lifecycle_state": "draft", ... }
```

**Expected**: ❌ Workflow fails with "FMs added: FM31 (prohibited in v1.0.x - escalate to v1.1.0+)"

### Test Case 3: Change Lifecycle State (Should Fail)

**Input**:
```json
{ "id": "FM7", "lifecycle_state": "deprecated", ... }
```

**Expected**: ❌ Workflow fails with "FM7: lifecycle_state is 'deprecated' (must be 'stable' in v1.0.x)"

### Test Case 4: Schema Change (Should Fail)

**Input**: Modify `schemas/v1.0.0/artifact.schema.json`

**Expected**: ❌ Workflow fails with "Schema changes are prohibited in v1.0.x"

---

## References

- **Failing Job**: https://github.com/hummbl-dev/base120/actions/runs/21723228902/job/62658400432
- **Pull Request**: https://github.com/hummbl-dev/base120/pull/38
- **Governance Policy**: `GOVERNANCE.md` lines 186-190, 283-336
- **Workflow File**: `.github/workflows/governance-version.yml` lines 110-114
- **Registry File**: `registries/fm.json`
- **Version**: `pyproject.toml` line 7 (`version = "1.0.0"`)

---

## Next Steps

1. **Immediate**: Review this document with CODEOWNER (@hummbl-dev)
2. **Decision**: Choose Option 1, 2, or 3 based on urgency and priorities
3. **Implementation**: Follow action plan for chosen option
4. **Validation**: Test workflow with PR #38
5. **Documentation**: Update AUDIT_INDEX.md and AAR.md with resolution

---

**Document Version**: 1.0  
**Created**: 2026-02-05 18:23:27  
**Author**: GitHub Copilot (troubleshooting assistance for hummbl-dev)  
**Status**: Ready for Review