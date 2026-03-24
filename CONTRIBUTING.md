# Contributing to Base120

Base120 v1.0.x is a **frozen specification**. This means the scope of accepted contributions is intentionally narrow.

## What's Welcome

- Documentation improvements and typo fixes
- Golden corpus additions (new test cases in `tests/corpus/`)
- CI workflow improvements
- Security fixes
- Observability enhancements (must be opt-in and semantics-preserving)

## What's Not Accepted in v1.0.x

- Schema changes (`schemas/v1.0.0/`)
- Registry modifications (`registries/`)
- Breaking changes to validation behavior
- New runtime dependencies

These changes are planned for v1.1 and will be accepted on a feature branch.

## Process

1. Open an issue describing the change
2. Fork the repo and create a branch from `main`
3. Make your changes
4. Ensure CI passes: `pytest tests/`
5. Open a PR referencing the issue

All PRs are automatically classified by the governance CI workflows. See [GOVERNANCE.md](GOVERNANCE.md) for change class definitions and review requirements.
