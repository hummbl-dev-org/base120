#!/usr/bin/env python3
"""Extract deterministic fields from pytest JSON report for hash comparison."""

import json
import sys


def extract_deterministic_fields(input_path: str, output_path: str) -> None:
    """Extract only deterministic fields from pytest JSON report.

    Args:
        input_path: Path to the pytest JSON report
        output_path: Path to write the cleaned JSON
    """
    with open(input_path) as f:
        data = json.load(f)

    # Extract deterministic fields only (no timing, no duration)
    results = {
        'summary': data['summary'],
        'tests': [
            {
                'nodeid': t['nodeid'],
                'outcome': t['outcome'],
                'call': t.get('call', {}).get('longrepr', '')
            }
            for t in data['tests']
        ]
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, sort_keys=True, indent=2)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.json> <output.json>", file=sys.stderr)
        sys.exit(1)

    extract_deterministic_fields(sys.argv[1], sys.argv[2])
