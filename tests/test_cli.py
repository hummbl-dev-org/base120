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

"""Tests for base120.cli — argument parsing and command handlers."""

from __future__ import annotations

import pytest

from base120.cli import build_parser, main


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

class TestParser:
    def test_list_no_args(self):
        parser = build_parser()
        args = parser.parse_args(["list"])
        assert args.command == "list"
        assert args.family is None

    def test_list_with_family(self):
        parser = build_parser()
        args = parser.parse_args(["list", "--family", "DE"])
        assert args.family == "DE"

    def test_get_code(self):
        parser = build_parser()
        args = parser.parse_args(["get", "P6"])
        assert args.code == "P6"

    def test_prompt_code_and_problem(self):
        parser = build_parser()
        args = parser.parse_args(["prompt", "P6", "my problem"])
        assert args.code == "P6"
        assert args.problem == "my problem"

    def test_families_command(self):
        parser = build_parser()
        args = parser.parse_args(["families"])
        assert args.command == "families"


# ---------------------------------------------------------------------------
# Command execution
# ---------------------------------------------------------------------------

class TestMain:
    def test_list_all(self, capsys: pytest.CaptureFixture[str]):
        rc = main(["list"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "P1" in out
        assert "SY20" in out

    def test_list_family(self, capsys: pytest.CaptureFixture[str]):
        rc = main(["list", "--family", "DE"])
        assert rc == 0
        out = capsys.readouterr().out
        # Should include DE codes and NOT other family codes as operators
        assert "DE1" in out
        assert "DE20" in out

    def test_list_unknown_family(self, capsys: pytest.CaptureFixture[str]):
        rc = main(["list", "--family", "ZZ"])
        assert rc == 1

    def test_get_valid(self, capsys: pytest.CaptureFixture[str]):
        rc = main(["get", "P6"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "P6" in out
        assert "Perspective" in out or "P" in out

    def test_get_invalid(self, capsys: pytest.CaptureFixture[str]):
        rc = main(["get", "XX99"])
        assert rc == 1

    def test_prompt_valid(self, capsys: pytest.CaptureFixture[str]):
        rc = main(["prompt", "P6", "how should we price this?"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "P6" in out
        assert "how should we price this?" in out
        assert "recommendation" in out

    def test_prompt_invalid_code(self, capsys: pytest.CaptureFixture[str]):
        rc = main(["prompt", "XX99", "test"])
        assert rc == 1

    def test_families(self, capsys: pytest.CaptureFixture[str]):
        rc = main(["families"])
        assert rc == 0
        out = capsys.readouterr().out
        for fam in ("P", "IN", "CO", "DE", "RE", "SY"):
            assert fam in out
