# Package Identity Receipt

Date: 2026-06-28

## Decision

- Canonical package name: `base120`
- Import package: `base120`
- Console scripts: `base120`, `base120-mcp`
- Not canonical: `hummbl-base120`

## Evidence

- `pyproject.toml` declares `[project].name = "base120"`.
- `pyproject.toml` discovers Python packages with `include = ["base120*"]`.
- `base120/__init__.py` exposes the current SDK API and `__version__`.
- GitHub canonical repository is `hummbl-dev/base120`.

## Publication Status

Live PyPI probes on 2026-06-28 returned 404 for both candidates:

- `https://pypi.org/project/base120/`
- `https://pypi.org/project/hummbl-base120/`

Until a package distribution is published, public docs must advertise source
installation only and must not claim `pip install base120` availability.
