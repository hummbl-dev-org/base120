"""Base120 reasoning engine.

Loads all 120 operators from the canonical registry and provides:
  - get(code)             → Operator | None
  - list(family)          → list[Operator]  (ordered, filterable by family)
  - families()            → list[str]       (P, IN, CO, DE, RE, SY)
  - prompt(code, problem) → str             (system prompt for this operator+problem)
  - record(...)           → ApplyResult     (governance-loggable application record)

Zero third-party dependencies. Stdlib only.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from base120.models import ApplyResult, Operator

_DATA_DIR = Path(__file__).parent / "data"

# Canonical family order — display and CLI consistency.
FAMILIES: tuple[str, ...] = ("P", "IN", "CO", "DE", "RE", "SY")

FAMILY_NAMES: dict[str, str] = {
    "P":  "Perspective",
    "IN": "Inversion",
    "CO": "Composition",
    "DE": "Decomposition",
    "RE": "Recursion",
    "SY": "Synthesis",
}


@lru_cache(maxsize=1)
def _load_operators() -> dict[str, Operator]:
    """Load and cache all 120 operators from operators.json."""
    path = _DATA_DIR / "operators.json"
    with open(path, encoding="utf-8") as fh:
        records = json.load(fh)
    return {
        rec["code"]: Operator(
            code=rec["code"],
            name=rec["name"],
            transformation=rec["transformation"],
            definition=rec["definition"],
        )
        for rec in records
    }


def _family_sort_key(op: Operator) -> tuple[int, int]:
    """Sort key: canonical family order, then numeric suffix."""
    try:
        fam_idx = FAMILIES.index(op.transformation)
    except ValueError:
        fam_idx = len(FAMILIES)
    # Extract numeric suffix: "P6" → 6, "IN12" → 12
    suffix = "".join(c for c in op.code if c.isdigit())
    num = int(suffix) if suffix else 0
    return (fam_idx, num)


class Engine:
    """Base120 operator engine.

    Lazy-loads all 120 operators from the package data directory on first use.
    Thread-safe via lru_cache on the underlying loader.

    Usage::

        engine = Engine()
        op = engine.get("P6")
        prompt = engine.prompt("P6", "How should we price the certification tier?")
        result = engine.record("P6", "How should...", "Anchor to compliance officer POV", 0.85)
        result.to_tuple()  # OperatorTuple(id='P6', time='...', state='...', drift=0.15)
    """

    def get(self, code: str) -> Operator | None:
        """Look up an operator by code (e.g. "P6", "DE1").

        Returns None if the code is not in the registry.
        """
        return _load_operators().get(code)

    def list(self, family: str | None = None) -> list[Operator]:
        """Return operators, optionally filtered by family.

        Args:
            family: One of P, IN, CO, DE, RE, SY (case-insensitive).
                    None returns all 120 operators.

        Returns:
            Ordered list — canonical family order, then ascending numeric suffix.
        """
        ops = _load_operators()
        if family is not None:
            key = family.upper()
            result = [op for op in ops.values() if op.transformation == key]
        else:
            result = list(ops.values())
        return sorted(result, key=_family_sort_key)

    def families(self) -> list[str]:
        """Return the 6 canonical family codes in order."""
        return list(FAMILIES)

    def prompt(self, code: str, problem: str) -> str:
        """Generate a system prompt for applying this operator to a problem.

        Args:
            code:    Operator code, e.g. "P6".
            problem: The problem statement to reason about.

        Returns:
            A system prompt string suitable for any LLM.

        Raises:
            ValueError: If the code is not in the registry.
        """
        op = self.get(code)
        if op is None:
            raise ValueError(
                f"Unknown operator code: {code!r}. "
                f"Use engine.list() to see all 120 codes."
            )
        return (
            f"You are applying the Base120 reasoning operator "
            f"{op.code}: {op.name} ({op.transformation} family).\n\n"
            f"Operator definition: {op.definition}\n\n"
            f"Problem: {problem}\n\n"
            f"Apply this operator rigorously to the problem. "
            f"Return a JSON object with exactly these keys:\n"
            f'  "recommendation": string — your primary output\n'
            f'  "confidence": float 0.0–1.0 — your certainty\n'
            f'  "reasoning": string — key steps that led to the recommendation\n'
        )

    def record(
        self,
        code: str,
        problem: str,
        recommendation: str,
        confidence: float,
        **metadata: object,
    ) -> ApplyResult:
        """Record a completed operator application as a governance artifact.

        Args:
            code:           Operator code, e.g. "P6".
            problem:        The original problem statement.
            recommendation: The output of the application.
            confidence:     Certainty score 0.0–1.0.
            **metadata:     Arbitrary context to attach (model name, session id, etc.).

        Returns:
            ApplyResult — call .to_tuple() to emit a VERUM-aligned evidence record.

        Raises:
            ValueError: If the code is not in the registry.
            ValueError: If confidence is outside [0.0, 1.0].
        """
        op = self.get(code)
        if op is None:
            raise ValueError(f"Unknown operator code: {code!r}.")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                f"confidence must be between 0.0 and 1.0, got {confidence!r}."
            )
        return ApplyResult(
            code=op.code,
            name=op.name,
            problem=problem,
            recommendation=recommendation,
            confidence=confidence,
            metadata=dict(metadata),
        )
