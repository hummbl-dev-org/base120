"""
Baseline Snapshot Capture

Captures golden corpus validation outputs as versioned snapshots.
Stores with metadata (commit SHA, date, Base120 version, schema version).
"""

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from base120.validators.validate import validate_artifact


def get_git_sha() -> str:
    """Get current git commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def get_git_timestamp() -> str:
    """Get timestamp of current git commit."""
    try:
        result = subprocess.run(
            ["git", "show", "-s", "--format=%cI", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return datetime.now(timezone.utc).isoformat()


def capture_baseline(
    corpus_dir: Path,
    schema_path: Path,
    mappings_path: Path,
    err_registry_path: Path,
    output_dir: Path,
    snapshot_name: str | None = None,
) -> Path:
    """
    Capture baseline snapshot of golden corpus validation outputs.
    
    Args:
        corpus_dir: Path to tests/corpus directory
        schema_path: Path to artifact.schema.json
        mappings_path: Path to mappings.json
        err_registry_path: Path to err.json
        output_dir: Path to artifacts/golden_corpus_snapshots
        snapshot_name: Optional custom snapshot name (default: git SHA)
        
    Returns:
        Path to created snapshot file
    """
    # Load validation resources
    with open(schema_path) as f:
        schema = json.load(f)
    
    with open(mappings_path) as f:
        mappings = json.load(f)
    
    with open(err_registry_path) as f:
        err_registry = json.load(f)["registry"]
    
    # Collect validation outputs for all corpus files
    results = {
        "valid": {},
        "invalid": {},
    }
    
    # Process valid corpus
    valid_dir = corpus_dir / "valid"
    if valid_dir.exists():
        for corpus_file in sorted(valid_dir.glob("*.json")):
            with open(corpus_file) as f:
                artifact = json.load(f)
            
            errors = validate_artifact(artifact, schema, mappings, err_registry)
            results["valid"][corpus_file.name] = {
                "errors": errors,
                "artifact_id": artifact.get("id", "unknown"),
            }
    
    # Process invalid corpus
    invalid_dir = corpus_dir / "invalid"
    if invalid_dir.exists():
        for corpus_file in sorted(invalid_dir.glob("*.json")):
            with open(corpus_file) as f:
                artifact = json.load(f)
            
            errors = validate_artifact(artifact, schema, mappings, err_registry)
            results["invalid"][corpus_file.name] = {
                "errors": errors,
                "artifact_id": artifact.get("id", "unknown"),
            }
    
    # Create snapshot with metadata
    git_sha = get_git_sha()
    snapshot_id = snapshot_name or git_sha[:8]
    
    # Use fixed timestamp for deterministic testing
    if "BASE120_FIXED_TIMESTAMP" in os.environ:
        timestamp = os.environ["BASE120_FIXED_TIMESTAMP"]
    else:
        timestamp = get_git_timestamp()
    
    snapshot = {
        "snapshot_id": snapshot_id,
        "git_sha": git_sha,
        "timestamp": timestamp,
        "base120_version": "1.0.0",  # From pyproject.toml
        "schema_version": "v1.0.0",
        "results": results,
    }
    
    # Write snapshot to file
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot_file = output_dir / f"snapshot-{snapshot_id}.json"
    
    with open(snapshot_file, "w") as f:
        json.dump(snapshot, f, indent=2, sort_keys=True)
    
    return snapshot_file


def main():
    """CLI entry point for baseline capture."""
    import sys
    
    # Determine repository root
    root = Path(__file__).parent.parent.parent
    
    corpus_dir = root / "tests" / "corpus"
    schema_path = root / "schemas" / "v1.0.0" / "artifact.schema.json"
    mappings_path = root / "registries" / "mappings.json"
    err_registry_path = root / "registries" / "err.json"
    output_dir = root / "artifacts" / "golden_corpus_snapshots"
    
    # Check if required paths exist
    if not corpus_dir.exists():
        print(f"Error: Corpus directory not found: {corpus_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not schema_path.exists():
        print(f"Error: Schema not found: {schema_path}", file=sys.stderr)
        sys.exit(1)
    
    if not mappings_path.exists():
        print(f"Error: Mappings not found: {mappings_path}", file=sys.stderr)
        sys.exit(1)
    
    if not err_registry_path.exists():
        print(f"Error: Error registry not found: {err_registry_path}", file=sys.stderr)
        sys.exit(1)
    
    # Capture baseline
    snapshot_file = capture_baseline(
        corpus_dir=corpus_dir,
        schema_path=schema_path,
        mappings_path=mappings_path,
        err_registry_path=err_registry_path,
        output_dir=output_dir,
    )
    
    print(f"Baseline captured: {snapshot_file}")
    print(f"Snapshot size: {snapshot_file.stat().st_size} bytes")


if __name__ == "__main__":
    main()
