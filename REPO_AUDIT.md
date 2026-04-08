# Base120 Repository Audit Report

**Date:** 2026-04-08
**Auditor:** Claude (automated)
**Scope:** Full repository audit — code, tests, CI/CD, security, governance, documentation
**Commit:** 7172bb7 (main)

---

## Executive Summary

Base120 is a well-structured, governance-focused Python library implementing 120 mental models for structured reasoning. The codebase is small (~500 LOC of production Python), well-tested (49 tests, all passing), and has a comprehensive CI/CD pipeline with 9 GitHub Actions workflows. The project is at v1.0.0 with a frozen specification policy.

**Overall Assessment: HEALTHY** — with minor findings below.

---

## 1. Architecture & Code Quality

### Structure

```
base120/                    # Core library
  validators/               # Schema, mappings, errors, validate pipeline
  contract/                 # Contract unit validation + reporting
  drift/                    # Baseline capture + snapshot comparison
  observability.py          # Structured event emission
  cli.py                    # CLI entry point
```

### Findings

| # | Severity | Finding |
|---|----------|---------|
| 1.1 | **Low** | `base120/__init__.py` is empty — no public API re-exports. Users must import from `base120.validators.validate` directly. Consider adding a top-level `from base120.validators.validate import validate_artifact` for ergonomics. |
| 1.2 | **Info** | `validate_artifact` deduplication uses a side-effect-in-comprehension pattern: `[x for x in sorted(errs) if not (x in seen or seen.add(x))]`. This works but is non-obvious. A clearer alternative: `list(dict.fromkeys(sorted(errs)))`. |
| 1.3 | **Info** | The `_emit_event` function does a lazy import (`from base120.observability import create_validator_event`) inside the function body. This is intentional to keep observability opt-in but could cause import errors to be silently swallowed. |
| 1.4 | **Low** | `base120/drift/__init__.py` is empty — no re-exports from submodules. |
| 1.5 | **Info** | `_compare_semver` doesn't handle pre-release tags (e.g., `v1.0.0-rc.1`). Acceptable for v1.0.x frozen spec but may need attention for v1.1+. |
| 1.6 | **Info** | The `_has_cycle` DFS function mutates `path` list in a non-trivial way (clearing and re-extending) which could be fragile if the code is refactored. |

---

## 2. Security Audit

### Findings

| # | Severity | Finding |
|---|----------|---------|
| 2.1 | **Pass** | No hardcoded secrets, API keys, tokens, or passwords found anywhere in the repository. |
| 2.2 | **Pass** | No use of `eval()`, `exec()`, `os.system()`, or `subprocess` with `shell=True`. The one `subprocess.run()` in `drift/capture_baseline.py` uses list args (safe). |
| 2.3 | **Pass** | No SQL, no command injection, no path traversal vulnerabilities. |
| 2.4 | **Pass** | No `.env` files or credentials committed. `.gitignore` appropriately excludes `contract_report.json` and drift reports. |
| 2.5 | **Pass** | `SECURITY.md` is well-written with clear disclosure process, scope, and guarantees. |
| 2.6 | **Pass** | Apache 2.0 license is properly declared in `LICENSE` and referenced in `README.md` and `pyproject.toml`. |
| 2.7 | **Low** | `BASE120_FIXED_TIMESTAMP` env var in `observability.py` allows overriding timestamps. This is documented and used only for testing determinism. Acceptable, but production deployments should ensure this isn't set. |
| 2.8 | **Info** | No cryptographic signing of releases or artifacts (noted in `SECURITY.md` as planned for v1.1.0). |
| 2.9 | **Pass** | Minimal dependency surface: only `jsonschema>=4.0` at runtime. Low supply chain risk. |
| 2.10 | **Medium** | `registries/registry-hashes.json` contains placeholder strings (`<hash_fm>`, `<hash_err>`, `<hash_map>`) instead of actual SHA-256 hashes. This undermines registry integrity verification. |

---

## 3. Test Suite

### Summary

- **49 tests**, all passing
- **5 test modules**: test_corpus, test_observability, test_cli, test_contract, test_drift
- **Test runtime**: ~0.9s

### Coverage Areas

| Module | Tests | Coverage Assessment |
|--------|-------|---------------------|
| `validators/` | test_corpus (2), test_observability (14) | Good — covers valid/invalid corpus, FM30 dominance, event emission, backward compat |
| `contract/` | test_contract (20) | Excellent — semver, failure graph cycles, metadata, datetime parsing, warnings |
| `drift/` | test_drift (7) | Good — baseline capture, no-drift, encoding drift, add/remove files, reports |
| `cli.py` | test_cli (6) | Good — valid/invalid contracts, file-not-found, invalid JSON, default output |

### Findings

| # | Severity | Finding |
|---|----------|---------|
| 3.1 | **Low** | No `conftest.py` — shared fixtures (SCHEMA, MAPPINGS, ERR_REGISTRY) are duplicated across test files via module-level code. A shared conftest would reduce duplication. |
| 3.2 | **Info** | `test_dynamic_timestamp_without_env_var` relies on `time.sleep(0.01)` for timestamp differentiation, which is inherently flaky (noted in test comment). |
| 3.3 | **Low** | No negative test for the CLI `main()` entry point when called as `__main__`. |
| 3.4 | **Info** | Golden corpus is small (1 valid, 3 invalid cases). More corpus cases would strengthen the spec guarantee. |

---

## 4. CI/CD Pipeline

### Workflows (9 total)

| Workflow | Trigger | Purpose | Status |
|----------|---------|---------|--------|
| `ci.yml` | push/PR to main | Tests on Python 3.11, 3.12 | OK |
| `base120.yml` | push/PR to main | Tests on Python 3.13 + mirror guard | OK |
| `guardrails.yml` | push/PR/dispatch | Run full pytest | OK |
| `governance-invariants.yml` | push/PR/dispatch | 3-run determinism check | OK |
| `governance-classifier.yml` | PR opened/sync | Auto-classify change type | OK |
| `governance-audit.yml` | PR/dispatch | Verify audit trail | OK |
| `governance-version.yml` | PR/dispatch | Enforce v1.0.x freeze | OK |
| `drift-detection.yml` | push/PR/schedule/dispatch | Semantic drift detection | OK |
| `mirror-conformance.yml` | workflow_call | Reusable mirror validation | OK |
| `verify-seed.yml` | push/PR on artifacts/compliance | Verify seed hash | OK |

### Findings

| # | Severity | Finding |
|---|----------|---------|
| 4.1 | **Medium** | `ci.yml` uses `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683` (pinned SHA) but `actions/setup-python@v5` (unpinned tag). Inconsistent pinning strategy — either pin all to SHA or all to major tags. |
| 4.2 | **Medium** | Most other workflows use `actions/checkout@v6` and `actions/setup-python@v6` (major tag only). The `ci.yml` workflow still references checkout v4.2.2 SHA and setup-python v5, making it inconsistent with the rest. |
| 4.3 | **Low** | `ci.yml` tests Python 3.11 and 3.12, while `base120.yml`/`guardrails.yml`/`governance-invariants.yml` test Python 3.13 only. There's no workflow testing 3.13 in a matrix or 3.11/3.12 in the other workflows. Consider unifying. |
| 4.4 | **Info** | `drift-detection.yml` has `contents: write` permission. This is needed for auto-committing baselines but is broader than necessary for the PR detection job. Consider splitting into separate jobs with different permissions. |
| 4.5 | **Low** | `guardrails.yml` duplicates what `ci.yml` and `base120.yml` already do (run pytest). This creates unnecessary CI minutes. |
| 4.6 | **Info** | `governance-classifier.yml` has a logic bug: the "potential-breaking" check triggers for *any* Python file change + existence of test_corpus.py, which would always be true. This check fires before more specific checks but gets overridden by them. However, if only a non-validator Python file changes (e.g., `cli.py`), it would still be classified as `potential-breaking`. |

---

## 5. Dependencies

| Dependency | Version | Purpose | Risk |
|------------|---------|---------|------|
| `jsonschema` | >=4.0 | JSON Schema validation | Low — well-maintained, widely used |
| `pytest` | >=8.3.4 (test) | Test framework | None — test-only |
| `pytest-json-report` | >=1.5.0 (test) | JSON test reports | None — test-only |
| `setuptools` | >=61.0 (build) | Package building | Low |

**Assessment**: Minimal dependency surface. Dependabot is configured for both pip and GitHub Actions. Good practice.

---

## 6. Documentation

### Files Reviewed

- `README.md` — Clear, well-structured, includes badges, examples, and ecosystem links
- `SECURITY.md` — Comprehensive vulnerability disclosure policy
- `CONTRIBUTING.md` — Brief but functional
- `GOVERNANCE.md` — Extensive governance framework (29K)
- `docs/` — 11 documentation files covering spec, contracts, observability, drift detection

### Findings

| # | Severity | Finding |
|---|----------|---------|
| 6.1 | **Low** | `README.md` references `base120 validate-contract path/to/contract.json` but the CLI also writes a report file (default: `contract_report.json`). This isn't mentioned in the quick usage section. |
| 6.2 | **Info** | Several large audit/operational files at repo root add clutter: `AAR.md` (42K), `AUDIT_INDEX.md` (27K), `COMMIT_AUDIT.md` (27K), `COMMIT_AUDIT_BASE120_VIEW.md` (13K), `DAY2_AUDIT.md` (4K), `SITREP.md` (28K), `TROUBLESHOOTING_JOB_62658400432.md` (13K). These could be moved to a `docs/audits/` subdirectory. |
| 6.3 | **Info** | Three `.patch` files at repo root (`0001-*.patch`, `0002-*.patch`, `0003-*.patch`) appear to be development artifacts. Consider removing or moving to `docs/patches/`. |
| 6.4 | **Info** | `base120_productization_matrix_v0.2.csv` and `base120_productization_summary_v0.2.md` at repo root are business planning files. Consider moving to `docs/`. |
| 6.5 | **Info** | `v1.1-*` directories contain early v1.1 planning/prototyping (toon parser, notes pipeline, CI scripts, architecture doc). These are uncommonly placed at repo root — consider a `proposals/` or `v1.1/` unified directory. |
| 6.6 | **Info** | `.github/copilot-instructions.md` is comprehensive and well-written. |

---

## 7. Repository Hygiene

### Findings

| # | Severity | Finding |
|---|----------|---------|
| 7.1 | **Low** | `base120.egg-info/` is committed to the repository. This is a build artifact and should be in `.gitignore`. |
| 7.2 | **Low** | `.gitignore` doesn't include `dist/`, `build/`, or `*.egg` patterns, which are standard Python build artifacts. |
| 7.3 | **Info** | No `py.typed` marker file for PEP 561 typed package support. |
| 7.4 | **Info** | No type checking configuration (`mypy.ini`, `pyrightconfig.json`). Type hints are used but not enforced. |
| 7.5 | **Info** | No linter/formatter configuration (`ruff`, `black`, `flake8`). Code style is consistent but not enforced by tooling. |
| 7.6 | **Info** | `pyproject.toml` declares `python_requires` is missing — should specify `>=3.11` per README badge. |
| 7.7 | **Low** | `CODEOWNERS` assigns all files to `@hummbl-dev` (the org). Consider assigning to specific maintainers for better accountability. |

---

## 8. Governance & Compliance

### Findings

| # | Severity | Finding |
|---|----------|---------|
| 8.1 | **Pass** | `GOVERNANCE.md` is thorough (750+ lines) covering versioning, change classes, invariants, and escalation. |
| 8.2 | **Pass** | CAES spec is pinned at v1.0.0 with SHA-256 hash verification. |
| 8.3 | **Pass** | Seed integrity verification workflow validates SHA-256 hashes against MRCC. |
| 8.4 | **Pass** | Golden corpus determinism is verified via 3-run hash comparison in CI. |
| 8.5 | **Info** | Governance audit workflow checks are currently soft warnings (not hard failures). This is documented as intentional for gradual adoption. |

---

## Summary of Findings by Severity

| Severity | Count | Description |
|----------|-------|-------------|
| **Medium** | 3 | CI action version pinning inconsistency; registry hash placeholders |
| **Low** | 10 | Minor code, test, CI, and hygiene improvements |
| **Info** | 17 | Informational observations, no action required |
| **Pass** | 10 | Positive findings — things done well |

---

## Recommended Actions (Priority Order)

1. **Fix registry hash placeholders** (2.10): Compute and store actual SHA-256 hashes in `registries/registry-hashes.json`.
2. **Fix CI action pinning inconsistency** (4.1, 4.2): Align `ci.yml` checkout/setup-python versions with other workflows.
3. **Add `base120.egg-info/` to `.gitignore`** (7.1): Standard Python build artifact should not be committed.
4. **Add `python_requires=">=3.11"` to `pyproject.toml`** (7.6): Match documented requirement.
5. **Add standard Python patterns to `.gitignore`** (7.2): `dist/`, `build/`, `*.egg`.
6. **Consider consolidating CI workflows** (4.3, 4.5): `guardrails.yml` duplicates existing CI.
7. **Consider organizing root-level files** (6.2-6.5): Move audit docs, patches, planning files into subdirectories.
