"""MCP resources for Music Assistant."""

from __future__ import annotations

import json

from fastmcp import Context

from music_assistant_mcp.serializers import serialize_player


def register(mcp):
    @mcp.resource("ma://players")
    async def players_resource(ctx: Context) -> str:
        """All players with their current state."""
        client = ctx.request_context.lifespan_context["client"]
        players = client.players.players
        return json.dumps([serialize_player(p) for p in players], indent=2)

    @mcp.resource("ma://library/stats")
    async def library_stats_resource(ctx: Context) -> str:
        """Library statistics: counts of tracks, albums, artists, and playlists."""
        client = ctx.request_context.lifespan_context["client"]
        stats = {
            "tracks": await client.music.track_count(),
            "albums": await client.music.album_count(),
            "artists": await client.music.artist_count(),
            "playlists": await client.music.playlist_count(),
        }
        return json.dumps(stats, indent=2)

    @mcp.tool()
    async def get_players(ctx: Context) -> str:
        """Get all players with their current state."""
        client = ctx.request_context.lifespan_context["client"]
        players = client.players.players
        return json.dumps([serialize_player(p) for p in players], indent=2)

    @mcp.tool()
    async def get_library_stats(ctx: Context) -> str:
        """Get library statistics: counts of tracks, albums, artists, and playlists."""
        client = ctx.request_context.lifespan_context["client"]
        stats = {
            "tracks": await client.music.track_count(),
            "albums": await client.music.album_count(),
            "artists": await client.music.artist_count(),
            "playlists": await client.music.playlist_count(),
        }
        return json.dumps(stats, indent=2)
