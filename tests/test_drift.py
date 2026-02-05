"""
Tests for drift detection module.

Validates baseline capture, snapshot comparison, and drift reporting.
"""

import json
from pathlib import Path
import pytest

from base120.drift.capture_baseline import capture_baseline
from base120.drift.compare import compare_snapshots, DriftType


ROOT = Path(__file__).parent.parent
CORPUS = ROOT / "tests" / "corpus"
SCHEMA = ROOT / "schemas" / "v1.0.0" / "artifact.schema.json"
MAPPINGS = ROOT / "registries" / "mappings.json"
ERR_REGISTRY = ROOT / "registries" / "err.json"


def test_capture_baseline(tmp_path):
    """Test baseline snapshot capture."""
    output_dir = tmp_path / "snapshots"
    
    snapshot_file = capture_baseline(
        corpus_dir=CORPUS,
        schema_path=SCHEMA,
        mappings_path=MAPPINGS,
        err_registry_path=ERR_REGISTRY,
        output_dir=output_dir,
        snapshot_name="test-snapshot"
    )
    
    assert snapshot_file.exists()
    assert snapshot_file.name == "snapshot-test-snapshot.json"
    
    with open(snapshot_file) as f:
        snapshot = json.load(f)
    
    # Validate snapshot structure
    assert snapshot["snapshot_id"] == "test-snapshot"
    assert "git_sha" in snapshot
    assert "timestamp" in snapshot
    assert snapshot["base120_version"] == "1.0.0"
    assert snapshot["schema_version"] == "v1.0.0"
    assert "results" in snapshot
    assert "valid" in snapshot["results"]
    assert "invalid" in snapshot["results"]
    
    # Validate corpus results
    assert "valid-basic.json" in snapshot["results"]["valid"]
    assert snapshot["results"]["valid"]["valid-basic.json"]["errors"] == []


def test_compare_no_drift(tmp_path):
    """Test comparison with identical snapshots."""
    output_dir = tmp_path / "snapshots"
    
    # Capture baseline
    baseline = capture_baseline(
        corpus_dir=CORPUS,
        schema_path=SCHEMA,
        mappings_path=MAPPINGS,
        err_registry_path=ERR_REGISTRY,
        output_dir=output_dir,
        snapshot_name="baseline"
    )
    
    # Capture current (same as baseline)
    current = capture_baseline(
        corpus_dir=CORPUS,
        schema_path=SCHEMA,
        mappings_path=MAPPINGS,
        err_registry_path=ERR_REGISTRY,
        output_dir=output_dir,
        snapshot_name="current"
    )
    
    # Compare
    report = compare_snapshots(baseline, current)
    
    assert not report.has_drift()
    assert not report.has_breaking_drift()
    assert len(report.drift_items) == 0


def test_compare_encoding_drift(tmp_path):
    """Test detection of encoding drift."""
    output_dir = tmp_path / "snapshots"
    
    # Capture baseline
    baseline = capture_baseline(
        corpus_dir=CORPUS,
        schema_path=SCHEMA,
        mappings_path=MAPPINGS,
        err_registry_path=ERR_REGISTRY,
        output_dir=output_dir,
        snapshot_name="baseline"
    )
    
    # Modify baseline to simulate drift
    with open(baseline) as f:
        modified = json.load(f)
    
    modified["snapshot_id"] = "modified"
    modified["results"]["valid"]["valid-basic.json"]["errors"] = ["ERR-TEST-001"]
    
    modified_file = output_dir / "snapshot-modified.json"
    with open(modified_file, "w") as f:
        json.dump(modified, f)
    
    # Compare
    report = compare_snapshots(baseline, modified_file)
    
    assert report.has_drift()
    assert report.has_breaking_drift()
    assert len(report.drift_items) == 1
    
    drift_item = report.drift_items[0]
    assert drift_item.drift_type == DriftType.ENCODING_CHANGE
    assert drift_item.file_name == "valid-basic.json"
    assert drift_item.category == "valid"
    assert drift_item.baseline_errors == []
    assert drift_item.current_errors == ["ERR-TEST-001"]


def test_compare_new_corpus_file(tmp_path):
    """Test detection of new corpus file."""
    output_dir = tmp_path / "snapshots"
    
    # Capture baseline
    baseline = capture_baseline(
        corpus_dir=CORPUS,
        schema_path=SCHEMA,
        mappings_path=MAPPINGS,
        err_registry_path=ERR_REGISTRY,
        output_dir=output_dir,
        snapshot_name="baseline"
    )
    
    # Modify to add new file
    with open(baseline) as f:
        modified = json.load(f)
    
    modified["snapshot_id"] = "modified"
    modified["results"]["valid"]["new-test.json"] = {
        "artifact_id": "new-artifact",
        "errors": []
    }
    
    modified_file = output_dir / "snapshot-modified.json"
    with open(modified_file, "w") as f:
        json.dump(modified, f)
    
    # Compare
    report = compare_snapshots(baseline, modified_file)
    
    assert report.has_drift()
    assert not report.has_breaking_drift()  # Adding files is non-breaking
    assert len(report.drift_items) == 1
    
    drift_item = report.drift_items[0]
    assert drift_item.drift_type == DriftType.NEW_CORPUS_FILE
    assert drift_item.file_name == "new-test.json"
    assert drift_item.category == "valid"
    assert drift_item.baseline_errors is None
    assert drift_item.current_errors == []


def test_compare_removed_corpus_file(tmp_path):
    """Test detection of removed corpus file."""
    output_dir = tmp_path / "snapshots"
    
    # Capture baseline
    baseline = capture_baseline(
        corpus_dir=CORPUS,
        schema_path=SCHEMA,
        mappings_path=MAPPINGS,
        err_registry_path=ERR_REGISTRY,
        output_dir=output_dir,
        snapshot_name="baseline"
    )
    
    # Modify to remove file
    with open(baseline) as f:
        modified = json.load(f)
    
    modified["snapshot_id"] = "modified"
    del modified["results"]["valid"]["valid-basic.json"]
    
    modified_file = output_dir / "snapshot-modified.json"
    with open(modified_file, "w") as f:
        json.dump(modified, f)
    
    # Compare
    report = compare_snapshots(baseline, modified_file)
    
    assert report.has_drift()
    assert not report.has_breaking_drift()  # Removing files is non-breaking
    assert len(report.drift_items) == 1
    
    drift_item = report.drift_items[0]
    assert drift_item.drift_type == DriftType.REMOVED_CORPUS_FILE
    assert drift_item.file_name == "valid-basic.json"
    assert drift_item.category == "valid"
    assert drift_item.baseline_errors == []
    assert drift_item.current_errors is None


def test_drift_report_markdown():
    """Test markdown report generation."""
    from base120.drift.compare import DriftReport, DriftItem
    
    report = DriftReport(baseline_id="abc123", current_id="def456")
    
    # No drift case
    md = report.to_markdown()
    assert "No drift detected" in md
    assert "abc123" in md
    assert "def456" in md
    
    # With drift
    report.add_drift(DriftItem(
        drift_type=DriftType.ENCODING_CHANGE,
        file_name="test.json",
        category="valid",
        baseline_errors=[],
        current_errors=["ERR-001"],
        description="Output changed"
    ))
    
    md = report.to_markdown()
    assert "Breaking drift detected" in md
    assert "test.json" in md
    assert "encoding_change" in md


def test_drift_report_dict():
    """Test dictionary serialization."""
    from base120.drift.compare import DriftReport, DriftItem
    
    report = DriftReport(baseline_id="abc123", current_id="def456")
    report.add_drift(DriftItem(
        drift_type=DriftType.ENCODING_CHANGE,
        file_name="test.json",
        category="valid",
        baseline_errors=[],
        current_errors=["ERR-001"],
        description="Output changed"
    ))
    
    data = report.to_dict()
    
    assert data["baseline_id"] == "abc123"
    assert data["current_id"] == "def456"
    assert data["has_drift"] is True
    assert data["has_breaking_drift"] is True
    assert data["drift_count"] == 1
    assert len(data["drift_items"]) == 1
    assert data["drift_items"][0]["drift_type"] == "encoding_change"
