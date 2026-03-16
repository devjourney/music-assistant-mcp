# Changelog

## 0.1.2 — 2025-03-15

- Fixed duplicate `get_players` tool registration in `resources.py` that caused tools to be dropped

## 0.1.1 — 2025-03-15

- Fixed CI: moved dev dependencies from `[project.optional-dependencies]` to `[dependency-groups]` so `uv sync --dev` installs them correctly
- Fixed CI: suppressed `ruff` E402 lint errors for intentionally-late imports in `server.py`
- Fixed CI: allowed pytest to pass when no tests are collected (exit code 5)
- Upgraded GitHub Actions to v5 (`actions/checkout`, `astral-sh/setup-uv`, `actions/upload-artifact`, `actions/download-artifact`)

## 0.1.0 — 2025-03-15

Initial release.

- 27 tools across 5 modules: search, library, playback, queue, playlists
- 2 resources: `ma://players`, `ma://library/stats`
- Bearer token authentication via `MA_TOKEN`
- `uvx` / `pip install` compatible entry point
