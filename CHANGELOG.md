# Changelog

## 0.3.0 — 2026-03-22

- **BREAKING**: Replaced `get_item_children` with dedicated tools for clarity (19 → 20 tools)
  - `get_album_tracks` — get all tracks on an album (takes `item_id`, `provider`)
  - `get_artist_details` — get albums or top tracks for an artist (use `detail_type` param: `albums` or `top_tracks`)
- **BREAKING**: `manage_playlist_tracks` now accepts a `list` action to retrieve playlist tracks, replacing the need for a separate tool
- **BREAKING**: All tool parameters now use `Annotated[..., Field(description=...)]` instead of docstring `Args:` blocks for richer schema descriptions in MCP clients
- **BREAKING**: `media_types` parameters on `search`, `get_recently_played`, and `get_library` are now `list[Literal["track", "album", "artist", "playlist"]]` instead of `list[str]` for stricter validation
- All functionality from v0.2.2 is preserved — no features removed

## 0.2.2 — 2026-03-19

- Fixed `TypeError` when using default stdio transport: `host` and `port` args are now only passed for `streamable-http`

## 0.2.1 — 2026-03-19

- Added `streamable-http` transport support via `MA_MCP_TRANSPORT` env var (default: `stdio`)
- Added `MA_MCP_HOST` and `MA_MCP_PORT` env vars for configuring the HTTP transport (default: `0.0.0.0:8000`)

## 0.2.0 — 2026-03-16

- **BREAKING**: Consolidated 39 tools down to 18 using action parameters to stay within MCP client tool limits
  - `get_library` replaces `get_library_artists/albums/tracks/playlists` — use `media_type` param
  - `get_item_children` replaces `get_album_tracks`, `get_artist_albums`, `get_artist_toptracks`, `get_playlist_tracks` — use `child_type` param
  - `player_control` replaces 12 individual player tools — use `action` param (play, pause, stop, next, previous, seek, volume, mute, power, group, ungroup)
  - `queue_control` replaces `queue_clear/shuffle/repeat` — use `action` param
  - `manage_favorites` replaces `add_to_favorites/remove_from_favorites` — use `action` param
  - `manage_playlist_tracks` replaces `add_playlist_tracks/remove_playlist_tracks` — use `action` param
- Added `get_server_info` tool: MCP server version, Music Assistant backend details, connected providers, and tool count
- All functionality from v0.1.3 is preserved — no features removed

## 0.1.3 — 2026-03-15

- Added 11 new tools (27 → 38):
  - **Playlists**: `get_playlist_tracks` — list tracks in a playlist
  - **Discovery**: `get_artist_toptracks`, `get_similar_tracks`, `get_recommendations`
  - **Favorites**: `add_to_favorites`, `remove_from_favorites`
  - **Playback**: `player_play`, `player_pause`, `player_volume_mute`, `player_group`, `player_ungroup`

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
