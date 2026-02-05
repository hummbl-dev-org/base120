"""
Snapshot Comparison and Drift Detection

Compares current golden corpus outputs against historical baseline snapshots.
Detects encoding changes, semantic differences, and generates drift reports.
"""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class DriftType(Enum):
    """Types of drift that can be detected."""
    ENCODING_CHANGE = "encoding_change"  # Same input, different output
    SEMANTIC_CHANGE = "semantic_change"  # Structural differences in output
    NEW_CORPUS_FILE = "new_corpus_file"  # New test case added
    REMOVED_CORPUS_FILE = "removed_corpus_file"  # Test case removed
    NO_DRIFT = "no_drift"  # No changes detected


@dataclass
class DriftItem:
    """Represents a single drift detection."""
    drift_type: DriftType
    file_name: str
    category: str  # "valid" or "invalid"
    baseline_errors: list[str] | None
    current_errors: list[str] | None
    description: str


class DriftReport:
    """Container for drift detection results."""
    
    def __init__(self, baseline_id: str, current_id: str):
        self.baseline_id = baseline_id
        self.current_id = current_id
        self.drift_items: list[DriftItem] = []
    
    def add_drift(self, item: DriftItem):
        """Add a drift item to the report."""
        self.drift_items.append(item)
    
    def has_drift(self) -> bool:
        """Check if any drift was detected."""
        return any(
            item.drift_type != DriftType.NO_DRIFT 
            for item in self.drift_items
        )
    
    def has_breaking_drift(self) -> bool:
        """Check if breaking drift was detected (encoding/semantic changes)."""
        return any(
            item.drift_type in (DriftType.ENCODING_CHANGE, DriftType.SEMANTIC_CHANGE)
            for item in self.drift_items
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary for JSON serialization."""
        return {
            "baseline_id": self.baseline_id,
            "current_id": self.current_id,
            "has_drift": self.has_drift(),
            "has_breaking_drift": self.has_breaking_drift(),
            "drift_count": len(self.drift_items),
            "drift_items": [
                {
                    "drift_type": item.drift_type.value,
                    "file_name": item.file_name,
                    "category": item.category,
                    "baseline_errors": item.baseline_errors,
                    "current_errors": item.current_errors,
                    "description": item.description,
                }
                for item in self.drift_items
            ]
        }
    
    def to_markdown(self) -> str:
        """Generate markdown report for PR comments."""
        lines = [
            "## 🔍 Semantic Drift Detection Report",
            "",
            f"**Baseline:** `{self.baseline_id}`",
            f"**Current:** `{self.current_id}`",
            "",
        ]
        
        if not self.has_drift():
            lines.extend([
                "✅ **No drift detected** - all golden corpus outputs match baseline.",
                ""
            ])
            return "\n".join(lines)
        
        # Summary
        drift_counts = {}
        for item in self.drift_items:
            drift_counts[item.drift_type] = drift_counts.get(item.drift_type, 0) + 1
        
        if self.has_breaking_drift():
            lines.append("⚠️ **Breaking drift detected** - corpus outputs have changed!")
        else:
            lines.append("ℹ️ **Non-breaking drift detected** - corpus files added/removed.")
        
        lines.extend(["", "### Drift Summary", ""])
        
        for drift_type, count in sorted(drift_counts.items(), key=lambda x: x[1], reverse=True):
            emoji = "⚠️" if drift_type in (DriftType.ENCODING_CHANGE, DriftType.SEMANTIC_CHANGE) else "ℹ️"
            lines.append(f"- {emoji} {drift_type.value.replace('_', ' ').title()}: {count}")
        
        # Detailed drift items
        if self.drift_items:
            lines.extend(["", "### Detailed Changes", ""])
            
            for item in self.drift_items:
                lines.append(f"#### {item.category}/{item.file_name}")
                lines.append(f"**Type:** {item.drift_type.value}")
                lines.append(f"**Description:** {item.description}")
                
                if item.baseline_errors is not None:
                    lines.append(f"**Baseline errors:** `{item.baseline_errors}`")
                if item.current_errors is not None:
                    lines.append(f"**Current errors:** `{item.current_errors}`")
                
                lines.append("")
        
        lines.extend([
            "---",
            "📚 See [docs/drift-detection.md](../docs/drift-detection.md) for recovery protocols.",
        ])
        
        return "\n".join(lines)


def compare_snapshots(baseline_path: Path, current_path: Path) -> DriftReport:
    """
    Compare two snapshots and detect drift.
    
    Args:
        baseline_path: Path to baseline snapshot JSON
        current_path: Path to current snapshot JSON
        
    Returns:
        DriftReport containing all detected drift
    """
    with open(baseline_path) as f:
        baseline = json.load(f)
    
    with open(current_path) as f:
        current = json.load(f)
    
    report = DriftReport(
        baseline_id=baseline["snapshot_id"],
        current_id=current["snapshot_id"]
    )
    
    # Compare each category (valid/invalid)
    for category in ["valid", "invalid"]:
        baseline_results = baseline["results"].get(category, {})
        current_results = current["results"].get(category, {})
        
        # Check for removed files
        for file_name in baseline_results:
            if file_name not in current_results:
                report.add_drift(DriftItem(
                    drift_type=DriftType.REMOVED_CORPUS_FILE,
                    file_name=file_name,
                    category=category,
                    baseline_errors=baseline_results[file_name]["errors"],
                    current_errors=None,
                    description=f"Corpus file removed from {category} set"
                ))
        
        # Check for new files
        for file_name in current_results:
            if file_name not in baseline_results:
                report.add_drift(DriftItem(
                    drift_type=DriftType.NEW_CORPUS_FILE,
                    file_name=file_name,
                    category=category,
                    baseline_errors=None,
                    current_errors=current_results[file_name]["errors"],
                    description=f"New corpus file added to {category} set"
                ))
        
        # Check for encoding/semantic changes in existing files
        for file_name in baseline_results:
            if file_name in current_results:
                baseline_errors = baseline_results[file_name]["errors"]
                current_errors = current_results[file_name]["errors"]
                
                if baseline_errors != current_errors:
                    # Determine if encoding or semantic change
                    # Encoding change: byte-for-byte different output
                    # Semantic change: structural difference (e.g., different error codes)
                    
                    # For now, treat all differences as encoding changes
                    # since we're comparing error lists which should be deterministic
                    report.add_drift(DriftItem(
                        drift_type=DriftType.ENCODING_CHANGE,
                        file_name=file_name,
                        category=category,
                        baseline_errors=baseline_errors,
                        current_errors=current_errors,
                        description=f"Validation output changed: baseline={baseline_errors}, current={current_errors}"
                    ))
    
    return report


def main():
    """CLI entry point for snapshot comparison."""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python -m base120.drift.compare <baseline_snapshot> <current_snapshot>")
        print("Example: python -m base120.drift.compare snapshot-abc123.json snapshot-def456.json")
        sys.exit(1)
    
    baseline_path = Path(sys.argv[1])
    current_path = Path(sys.argv[2])
    
    if not baseline_path.exists():
        print(f"Error: Baseline snapshot not found: {baseline_path}", file=sys.stderr)
        sys.exit(1)
    
    if not current_path.exists():
        print(f"Error: Current snapshot not found: {current_path}", file=sys.stderr)
        sys.exit(1)
    
    # Compare snapshots
    report = compare_snapshots(baseline_path, current_path)
    
    # Output results
    print(report.to_markdown())
    print()
    
    # Also save JSON report
    report_file = current_path.parent / f"drift-report-{report.current_id}.json"
    with open(report_file, "w") as f:
        json.dump(report.to_dict(), f, indent=2, sort_keys=True)
    
    print(f"JSON report saved: {report_file}")
    
    # Exit with non-zero if breaking drift detected
    if report.has_breaking_drift():
        sys.exit(1)


if __name__ == "__main__":
    main()
