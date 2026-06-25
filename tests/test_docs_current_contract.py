# Copyright 2024-2026 HUMMBL, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

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
    assert "should not claim PyPI availability" in flat_readme


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
        "docs/contract-units.md",
        "docs/observability.md",
    ]

    for relative in docs_to_check:
        assert "pip install base120" not in _read(relative)


def test_documented_sdk_version_matches_package_metadata() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]

    assert base120.__version__ == version
    assert version in _read("README.md")
    assert version in _read("docs/REPO_HEALTH.md")
