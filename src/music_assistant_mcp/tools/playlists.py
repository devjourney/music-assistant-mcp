"""Playlist management tools for Music Assistant."""

from __future__ import annotations

import json

from fastmcp import Context

from music_assistant_mcp.serializers import serialize_playlist, serialize_track


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
    async def add_playlist_tracks(
        ctx: Context,
        playlist_id: str,
        uris: list[str],
    ) -> str:
        """Add tracks to a playlist by URI.

        Args:
            playlist_id: The playlist ID (database ID).
            uris: List of track URIs to add.
        """
        client = ctx.request_context.lifespan_context["client"]
        await client.music.add_playlist_tracks(playlist_id, uris)
        return json.dumps({"status": "ok", "action": "add_tracks", "playlist_id": playlist_id, "count": len(uris)})

    @mcp.tool()
    async def remove_playlist_tracks(
        ctx: Context,
        playlist_id: str,
        positions: list[int],
    ) -> str:
        """Remove tracks from a playlist by position.

        Args:
            playlist_id: The playlist ID (database ID).
            positions: List of track positions (0-indexed) to remove.
        """
        client = ctx.request_context.lifespan_context["client"]
        await client.music.remove_playlist_tracks(playlist_id, tuple(positions))
        return json.dumps({"status": "ok", "action": "remove_tracks", "playlist_id": playlist_id, "count": len(positions)})

    @mcp.tool()
    async def get_playlist_tracks(
        ctx: Context,
        item_id: str,
        provider: str,
    ) -> str:
        """Get all tracks in a playlist.

        Args:
            item_id: Playlist ID.
            provider: Provider instance ID or domain.
        """
        client = ctx.request_context.lifespan_context["client"]
        tracks = await client.music.get_playlist_tracks(item_id, provider)
        return json.dumps([serialize_track(t) for t in tracks], indent=2)
