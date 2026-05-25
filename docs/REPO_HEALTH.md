# Repository Health Contract

## Ownership

- **Repository**: `hummbl-dev/base120`
- **Canonical URL**: `https://github.com/hummbl-dev/base120`
- **Owner**: HUMMBL Team
- **Stewardship scope**: Canonical Base120 registry, executable corpus contract, governance specs, v1 reference artifacts, and the active Python v2 SDK.

## Lifecycle

- **Status**: Active public repository with frozen v1 registry/corpus artifacts and an active Python v2 SDK (`base120` 2.0.0.dev0).
- **Default branch**: `main`.
- **Release posture**: The v1 validator runtime is retired. The current Python package exposes operator lookup, prompting, MCP serving, and VERUM-aligned ledger records; registry, corpus, governance, documentation, and CI hardening changes may continue through pull requests.
- **Archive trigger**: Archive only if the canonical Base120 registry and corpus contract move to another declared source of truth.

## Source Of Truth

- `Base120_Canonical_Model_Registry.yaml` is the canonical model registry.
- `registries/` contains registry data files that mirror or support the canonical model set.
- `tests/corpus/` is the canonical executable corpus path for Base120 contract artifacts.
- `docs/corpus-contract.md` and `mirrors/CONFORMANCE_CONTRACT.md` document the corpus contract for implementations and mirrors.
- `GOVERNANCE.md` and `docs/governance-decision-tree.md` define change classes and review expectations.
- `docs/contract-units.md` defines archived v1 contract unit structure and examples; the current v2 SDK does not ship the `base120 validate-contract` command.
- `base120/` contains the active v2 SDK package.

## Validation Contract

Run from the repository root unless noted.

```bash
python -m pip install --upgrade pip
pip install -e ".[test]"
pytest
python -m pytest tests/ -v
python -m pip wheel . --no-deps -w dist-smoke
```

Expected CI coverage:

- `.github/workflows/ci.yml` runs tests on Python 3.11 and 3.12.
- `.github/workflows/base120.yml` runs mirror-guard checks and tests on Python 3.13.
- `.github/workflows/guardrails.yml` runs guardrail validation on Python 3.13.
- `.github/workflows/mirror-conformance.yml` is a reusable mirror-conformance workflow for downstream implementations.

## Branch Protection Expectation

`main` should be treated as protected:

- All non-trivial changes should land through pull requests.
- Required checks should include the Python test matrix and corpus/guardrail validation where applicable.
- Schema, corpus, registry, or formal model changes should follow the review classes in `GOVERNANCE.md`.
- Direct pushes to `main` should be limited to emergency operator action.

## Known Operational Gaps

- GitHub branch protection is tracked centrally in `hummbl-dev/hummbl-dev#18`; do not overclaim required checks until that audit is updated.
- The Python v1 validator package is retired, while the v2 SDK is active pre-release. Keep README/API docs aligned with the actual `Engine`, `Ledger`, CLI, and MCP entry points.
- `docs/contract-units.md` and `docs/observability.md` are archived v1 validator contracts, not current v2 SDK API promises.
- `tests/test_corpus_contract.py` validates that `tests/corpus/` exists, has valid/invalid JSON artifacts, and has expected-error manifests for every invalid artifact.

## Fleet Scan Classification

Future fleet scans can classify this repository as:

- **Lifecycle**: active, v1 validator runtime retired, v2 SDK pre-release active
- **Visibility**: public
- **Primary function**: canonical Base120 registry, executable corpus contract, and active stdlib-only Python SDK
- **Validation entrypoint**: `pytest`
- **Primary metadata owner**: HUMMBL Team
