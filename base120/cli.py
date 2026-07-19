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

"""Base120 CLI.

Commands:
  base120 list                    — list all 120 operators
  base120 list --family DE        — list operators for one family
  base120 get P6                  — show one operator's details
  base120 prompt P6 "problem"     — generate a system prompt
  base120 families                — list the 6 families with descriptions

Stdlib only. Zero third-party dependencies.
"""

from __future__ import annotations

import argparse
import sys

from base120.engine import Engine, FAMILY_NAMES


def _cmd_list(engine: Engine, args: argparse.Namespace) -> int:
    family: str | None = args.family
    ops = engine.list(family=family)
    if not ops:
        print(f"No operators found for family {family!r}.", file=sys.stderr)
        return 1
    if family:
        fname = FAMILY_NAMES.get(family.upper(), family.upper())
        print(f"{fname} ({family.upper()}) — {len(ops)} operators\n")
    for op in ops:
        print(f"  {op.code:<6}  {op.name}")
    return 0


def _cmd_get(engine: Engine, args: argparse.Namespace) -> int:
    op = engine.get(args.code)
    if op is None:
        print(f"Unknown operator code: {args.code!r}", file=sys.stderr)
        return 1
    fname = FAMILY_NAMES.get(op.transformation, op.transformation)
    print(f"{op.code}: {op.name}")
    print(f"  Family:     {op.transformation} — {fname}")
    print(f"  Definition: {op.definition}")
    return 0


def _cmd_prompt(engine: Engine, args: argparse.Namespace) -> int:
    try:
        prompt = engine.prompt(args.code, args.problem)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(prompt)
    return 0


def _cmd_families(engine: Engine, _args: argparse.Namespace) -> int:
    for fam in engine.families():
        name = FAMILY_NAMES.get(fam, fam)
        ops = engine.list(family=fam)
        print(f"  {fam:<4}  {name:<16}  {len(ops)} operators")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="base120",
        description="Base120 — 120 reasoning operators for structured thinking.",
    )
    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = True

    # list
    p_list = sub.add_parser("list", help="List operators")
    p_list.add_argument(
        "--family",
        metavar="FAMILY",
        help="Filter by family: P, IN, CO, DE, RE, SY",
    )

    # get
    p_get = sub.add_parser("get", help="Show operator details")
    p_get.add_argument("code", help="Operator code, e.g. P6 or DE1")

    # prompt
    p_prompt = sub.add_parser("prompt", help="Generate a system prompt")
    p_prompt.add_argument("code", help="Operator code, e.g. P6")
    p_prompt.add_argument("problem", help="Problem statement to reason about")

    # families
    sub.add_parser("families", help="List the 6 operator families")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    engine = Engine()

    dispatch = {
        "list":     _cmd_list,
        "get":      _cmd_get,
        "prompt":   _cmd_prompt,
        "families": _cmd_families,
    }
    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(engine, args)


if __name__ == "__main__":
    sys.exit(main())
