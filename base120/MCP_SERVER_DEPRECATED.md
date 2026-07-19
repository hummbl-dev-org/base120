# DEPRECATED — Moved to monorepo

**This file is deprecated as of 2026-06-23.**

The canonical version of this MCP server now lives in the HUMMBL MCP monorepo:

    https://github.com/hummbl-dev/mcp-server
    packages/python/base120/mcp_server.py

## Why

All HUMMBL MCP servers (TypeScript and Python) have been consolidated
into a single monorepo at `hummbl-dev/mcp-server` for easier maintenance,
shared CI, and consistent tooling.

## What to do

- **If you installed via PyPI:** Use `pip install hummbl-mcp-base120`
  (published separately)
- **If you cloned this repo:** The MCP server is no longer here. Clone
  `hummbl-dev/mcp-server` instead
- **If you imported this file directly:** Update your imports to point
  to the monorepo package

## Backwards compatibility

This file is kept for historical reference. It will not receive updates.
The Base120 engine itself (`base120/` package) is unaffected and remains
in this repo.

Generated with Devin — 2026-06-23
