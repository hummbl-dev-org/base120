#!/usr/bin/env python3
"""Validate that registries/fm.json changes in v1.0.x are metadata-only.

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


def load_fm_registry(content: str) -> dict:
    """Load FM registry from JSON content."""
    return json.loads(content)


def validate_metadata_only_change(before_content: str, after_content: str) -> tuple[bool, list[str]]:
    """Validate that changes are metadata-only additions.

    Returns: (is_valid, error_messages)
    """
    errors = []

    before = load_fm_registry(before_content)
    after = load_fm_registry(after_content)

    before_fms = {fm['id']: fm for fm in before['registry']}
    after_fms = {fm['id']: fm for fm in after['registry']}

    # Check 1: FM count must be identical
    if len(before_fms) != len(after_fms):
        errors.append(f"FM count changed: {len(before_fms)} -> {len(after_fms)} (prohibited in v1.0.x)")

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
            continue

        before_fm = before_fms[fm_id]
        after_fm = after_fms[fm_id]

        # Check 4a: Name unchanged
        if before_fm.get('name') != after_fm.get('name'):
            errors.append(f"{fm_id}: Name changed (prohibited in v1.0.x)")

        # Check 4b: If lifecycle_state exists, must be "stable"
        if 'lifecycle_state' in after_fm and after_fm['lifecycle_state'] != 'stable':
            errors.append(
                f"{fm_id}: lifecycle_state is '{after_fm['lifecycle_state']}' (must be 'stable' in v1.0.x)"
            )

        # Check 4c: Core fields not removed
        for core_field in ['id', 'name']:
            if core_field in before_fm and core_field not in after_fm:
                errors.append(f"{fm_id}: Core field '{core_field}' removed (prohibited)")

    # Check 5: Version field unchanged
    if before.get('version') != after.get('version'):
        errors.append(
            f"Registry version changed: {before.get('version')} -> {after.get('version')} (must remain v1.0.0)"
        )

    return len(errors) == 0, errors


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <before_file> <after_file>", file=sys.stderr)
        sys.exit(1)

    before_file = Path(sys.argv[1])
    after_file = Path(sys.argv[2])

    is_valid, errors = validate_metadata_only_change(
        before_file.read_text(),
        after_file.read_text()
    )

    if is_valid:
        print("PASS: Registry changes are metadata-only additions (permitted in v1.0.x)")
        sys.exit(0)
    else:
        print("FAIL: Registry contains prohibited semantic changes")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
