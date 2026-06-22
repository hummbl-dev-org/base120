# CONSTITUTION.md — base120

**Status:** v0.1
**Steward:** HUMMBL Research Institute
**Approving human:** Reuben Bowlby
**Standard:** HUMMBL Repo Standard v0.1
**Source of record:** git

## 1. Identity

`hummbl-dev/base120` — 120 named mental models for structured reasoning across six transformation families (P/IN/CO/DE/RE/SY). Authoritative reference implementation with stdlib-only Python v2 SDK, CLI, append-only ledger, and MCP server.

- **Class:** spec
- **Visibility:** public
- **License:** Apache-2.0
- **Validation:** `python -m pytest tests/ -v`

## 2. Scope

This constitution operates under the HUMMBL Repo Standard (`hummbl-dev/hummbl-governance/docs/standards/HUMMBL_REPO_STANDARD.md`) and the operating-environment constitution on the host machine. This constitution may be stricter than both, never weaker.

## 3. Protected invariants

These invariants are constitutionally protected. They cannot be changed, weakened, or conditionally suspended without a constitutional amendment (§7), a KRINEIA receipt, and human approval.

1. **Canon count.** The registry defines exactly 120 operators across six families. SY1-SY20 fixed; SY21-SY24 moved to proposed queue.
2. **Canonical registry is source of truth.** Base120_Canonical_Model_Registry.yaml and registries/*.json are authoritative. SDK code, docs, and mirrors derive from them, never the reverse.
3. **Golden corpus determinism.** All changes preserve byte-for-byte reproducibility of tests/corpus/expected/ outputs.
4. **Stdlib-only runtime.** Production code in base120/ has zero third-party runtime dependencies.
5. **Python 3.11+.** The SDK requires >=3.11.
6. **Append-only ledger.** Ledger records are VERUM-aligned JSONL tuples, never mutated in place.
7. **Schema stability.** schemas/v1.0.0/*.schema.json are frozen v1 reference artifacts.
8. **License.** Apache-2.0, unchanged.

## 4. Normative files

The following files are normative. Edits require steward review (see `CODEOWNERS`):

- `CONSTITUTION.md`
- `KRINEIA.md`
- `hummbl.repo.yaml`
- `CODEOWNERS`
- `Base120_Canonical_Model_Registry.yaml`
- `registries/`
- `schemas/`
- `tests/corpus/`
- `AGENTS.md`

## 5. Authority

- **Steward:** HUMMBL Research Institute
- **Approving human:** Reuben Bowlby
- **Codeowners:** `CODEOWNERS`
- **Agent operating contract:** `AGENTS.md`
- **Receipt manifest:** `KRINEIA.md`

## 6. Receipt-triggering changes

The following changes require a KRINEIA receipt before admission:

- Any edit to Base120_Canonical_Model_Registry.yaml or registries/*.json
- Any change to operator count, IDs, family assignments, or names
- Any change to schemas/v1.0.0/*.schema.json
- Any change to the golden corpus (tests/corpus/) or expected outputs
- Any change to CONSTITUTION.md, KRINEIA.md, hummbl.repo.yaml, or CODEOWNERS
- Any release or version bump
- Any migration, retirement, or scope transfer

## 7. Amendment

Changes to this constitution require: a PR, an ADR under `docs/adr/`, a KRINEIA receipt, and human approval (Reuben Bowlby). Breaking changes bump this constitution's version (SemVer) and trigger a fleet re-audit of all repos consuming this repo's outputs.
