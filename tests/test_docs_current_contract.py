"""Public documentation checks for the current Base120 package surface."""

from __future__ import annotations

from pathlib import Path
import tomllib

import base120


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _flat(text: str) -> str:
    return " ".join(text.split())


def test_readme_advertises_current_sdk_surface() -> None:
    readme = _read("README.md")
    flat_readme = _flat(readme)

    unsupported_claims = [
        "Python code has been removed",
        "base120 validate-contract path/to",
        "from base120.validators",
        "from base120.observability",
        "pip install base120",
    ]
    for claim in unsupported_claims:
        assert claim not in readme

    assert "does not ship `base120 validate-contract`" in flat_readme
    assert "does not expose `base120.observability`" in flat_readme
    assert "from base120 import Engine, Ledger" in readme
    assert "base120 list" in readme
    assert "base120 get P6" in readme
    assert "base120 prompt P6" in readme
    assert "base120 families" in readme
    assert "source installation only until a package distribution exists" in flat_readme


def test_archived_validator_docs_are_marked_as_archived() -> None:
    archived_docs = [
        "docs/contract-units.md",
        "docs/observability.md",
    ]

    for relative in archived_docs:
        text = _read(relative)
        lower_text = text.lower()
        assert "archived v1 validator contract" in lower_text
        assert "current" in lower_text
        assert "v2 sdk does not" in lower_text


def test_current_docs_do_not_claim_pypi_install() -> None:
    docs_to_check = [
        "README.md",
        "llms.txt",
        "docs/contract-units.md",
        "docs/observability.md",
    ]

    for relative in docs_to_check:
        assert "pip install base120" not in _read(relative)
        assert "pypi.org/project/base120" not in _read(relative).lower()


def test_public_package_identity_is_unambiguous() -> None:
    readme = _read("README.md")
    llms = _read("llms.txt")
    receipt = _read("docs/PACKAGE_IDENTITY_RECEIPT.md")

    assert 'name = "base120"' in _read("pyproject.toml")
    assert "canonical package name is `base120`" in readme
    assert "`hummbl-base120` is not the canonical package name" in _flat(readme)
    assert "Package identity: base120" in llms
    assert "PyPI status: unpublished" in llms
    assert "canonical package name: `base120`" in receipt.lower()
    assert "not canonical: `hummbl-base120`" in receipt.lower()


def test_documented_sdk_version_matches_package_metadata() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]

    assert base120.__version__ == version
    assert version in _read("README.md")
    assert version in _read("docs/REPO_HEALTH.md")
