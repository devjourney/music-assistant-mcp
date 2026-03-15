"""Playback control tools for Music Assistant."""

from __future__ import annotations

import json

from fastmcp import Context

from music_assistant_mcp.serializers import serialize_player


def register(mcp):
    @mcp.tool()
    async def get_players(ctx: Context) -> str:
        """Get all available players and their current state."""
        client = ctx.request_context.lifespan_context["client"]
        players = client.players.players
        return json.dumps([serialize_player(p) for p in players], indent=2)

    @mcp.tool()
    async def player_play_pause(ctx: Context, player_id: str) -> str:
        """Toggle play/pause on a player.

        Args:
            player_id: The player ID.
        """
        client = ctx.request_context.lifespan_context["client"]
        await client.players.play_pause(player_id)
        return json.dumps({"status": "ok", "action": "play_pause", "player_id": player_id})

    @mcp.tool()
    async def player_stop(ctx: Context, player_id: str) -> str:
        """Stop playback on a player.

        Args:
            player_id: The player ID.
        """
        client = ctx.request_context.lifespan_context["client"]
        await client.players.stop(player_id)
        return json.dumps({"status": "ok", "action": "stop", "player_id": player_id})

    @mcp.tool()
    async def player_next(ctx: Context, player_id: str) -> str:
        """Skip to next track on a player.

        Args:
            player_id: The player ID.
        """
        client = ctx.request_context.lifespan_context["client"]
        await client.players.next_track(player_id)
        return json.dumps({"status": "ok", "action": "next", "player_id": player_id})

    @mcp.tool()
    async def player_previous(ctx: Context, player_id: str) -> str:
        """Go to previous track on a player.

        Args:
            player_id: The player ID.
        """
        client = ctx.request_context.lifespan_context["client"]
        await client.players.previous_track(player_id)
        return json.dumps({"status": "ok", "action": "previous", "player_id": player_id})

    @mcp.tool()
    async def player_volume(ctx: Context, player_id: str, level: int) -> str:
        """Set volume level on a player.

        Args:
            player_id: The player ID.
            level: Volume level 0-100.
        """
        client = ctx.request_context.lifespan_context["client"]
        await client.players.volume_set(player_id, level)
        return json.dumps({"status": "ok", "action": "volume_set", "player_id": player_id, "level": level})

    @mcp.tool()
    async def player_power(ctx: Context, player_id: str, powered: bool) -> str:
        """Turn a player on or off.

        Args:
            player_id: The player ID.
            powered: True to power on, False to power off.
        """
        client = ctx.request_context.lifespan_context["client"]
        await client.players.power(player_id, powered)
        return json.dumps({"status": "ok", "action": "power", "player_id": player_id, "powered": powered})

    @mcp.tool()
    async def player_seek(ctx: Context, player_id: str, position: int) -> str:
        """Seek to a position in the current track.

        Args:
            player_id: The player ID.
            position: Position in seconds.
        """
        client = ctx.request_context.lifespan_context["client"]
        await client.players.seek(player_id, position)
        return json.dumps({"status": "ok", "action": "seek", "player_id": player_id, "position": position})
