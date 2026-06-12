"""base120 — 120 reasoning operators for structured thinking.

Version 2 of the base120 Python SDK. Stdlib-only. Zero third-party runtime
dependencies. Tuple-native output aligned to the VERUM sovereignty model.

Quick start::

    from base120 import Engine

    engine = Engine()

    # Discover operators
    op = engine.get("P6")           # Operator(code='P6', name='Point-of-View Anchoring', ...)
    ops = engine.list(family="DE")  # 20 Decomposition operators

    # Generate a system prompt for any LLM
    prompt = engine.prompt("P6", "How should we price the certification tier?")

    # Record an application as a governance artifact
    result = engine.record("P6", "How should...", "Anchor to compliance officer POV", 0.85)
    t = result.to_tuple()  # OperatorTuple(id='P6', time='...Z', state='...', drift=0.15)
    # Append to the VERUM audit ledger
    from base120 import Ledger
    ledger = Ledger()
    ledger.append(t)                  # ~/.base120/ledger.jsonl
    high_drift = ledger.cut(0.5)      # entries with drift > 0.5

VERUM alignment:
  to_tuple() fields map to the 4 VERUM node fields:
    id    → who/what (operator code)
    time  → when     (UTC ISO-8601)
    state → current condition (recommendation)
    drift → deviation from setpoint (1.0 - confidence)

CLI::

    base120 list
    base120 list --family DE
    base120 get P6
    base120 prompt P6 "your problem here"
    base120 families

Apache 2.0. Copyright 2026 HUMMBL, LLC.
"""

from __future__ import annotations

from base120.engine import Engine, FAMILIES, FAMILY_NAMES
from base120.ledger import Ledger
from base120.models import ApplyResult, Operator, OperatorTuple

__version__ = "2.0.0"

__all__ = [
    "__version__",
    "Engine",
    "Ledger",
    "Operator",
    "ApplyResult",
    "OperatorTuple",
    "FAMILIES",
    "FAMILY_NAMES",
]
