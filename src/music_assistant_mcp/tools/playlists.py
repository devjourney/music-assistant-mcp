"""Playlist management tools for Music Assistant."""

from __future__ import annotations

import json
from typing import Literal

from fastmcp import Context

from music_assistant_mcp.serializers import serialize_playlist


def register(mcp):
    @mcp.tool()
    async def create_playlist(
        ctx: Context,
        name: str,
        provider: str | None = None,
    ) -> str:
        """Create a new playlist.

        Args:
            name: Name for the new playlist.
            provider: Provider instance ID or domain. Uses default if not specified.
        """
        client = ctx.request_context.lifespan_context["client"]
        playlist = await client.music.create_playlist(name, provider_instance_or_domain=provider)
        return json.dumps(serialize_playlist(playlist), indent=2)

    @mcp.tool()
    async def manage_playlist_tracks(
        ctx: Context,
        playlist_id: str,
        action: Literal["add", "remove"],
        uris: list[str] | None = None,
        positions: list[int] | None = None,
    ) -> str:
        """Add or remove tracks from a playlist.

        - add: requires uris (list of track URIs)
        - remove: requires positions (list of 0-indexed track positions)

        Args:
            playlist_id: The playlist ID (database ID).
            action: Action to perform: add or remove.
            uris: List of track URIs to add (for add action).
            positions: List of track positions to remove (for remove action).
        """
        client = ctx.request_context.lifespan_context["client"]
        if action == "add":
            await client.music.add_playlist_tracks(playlist_id, uris)
            return json.dumps({"status": "ok", "action": "add_tracks", "playlist_id": playlist_id, "count": len(uris)})
        else:
            await client.music.remove_playlist_tracks(playlist_id, tuple(positions))
            return json.dumps({"status": "ok", "action": "remove_tracks", "playlist_id": playlist_id, "count": len(positions)})
