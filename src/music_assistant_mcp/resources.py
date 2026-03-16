"""MCP resources for Music Assistant."""

from __future__ import annotations

import json
from importlib.metadata import version

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
    async def get_server_info(ctx: Context) -> str:
        """Get server information: MCP server version, Music Assistant backend details, and connected providers."""
        client = ctx.request_context.lifespan_context["client"]
        info = client.server_info
        tools = await mcp.list_tools()
        result = {
            "mcp_server": {
                "name": "music-assistant-mcp",
                "version": version("music-assistant-mcp"),
            },
            "music_assistant": {
                "server_version": info.server_version,
                "server_id": info.server_id,
                "base_url": info.base_url,
            },
            "providers": [
                {
                    "name": p.name,
                    "domain": p.domain,
                    "type": str(p.type),
                    "available": p.available,
                }
                for p in client.providers
            ],
            "tool_count": len(tools),
        }
        return json.dumps(result, indent=2)

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
