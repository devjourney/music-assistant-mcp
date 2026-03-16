"""Playback control tools for Music Assistant."""

from __future__ import annotations

import json
from typing import Literal

from fastmcp import Context

from music_assistant_mcp.serializers import serialize_player

PlayerAction = Literal[
    "play", "pause", "stop", "next", "previous",
    "seek", "volume", "mute", "power", "group", "ungroup",
]


def register(mcp):
    @mcp.tool()
    async def get_players(ctx: Context) -> str:
        """Get all available players and their current state."""
        client = ctx.request_context.lifespan_context["client"]
        players = client.players.players
        return json.dumps([serialize_player(p) for p in players], indent=2)

    @mcp.tool()
    async def player_control(
        ctx: Context,
        player_id: str,
        action: PlayerAction,
        position: int | None = None,
        level: int | None = None,
        muted: bool | None = None,
        powered: bool | None = None,
        target_player: str | None = None,
    ) -> str:
        """Control a player. Actions and their required parameters:

        - play, pause, stop, next, previous, ungroup: no extra params
        - seek: position (seconds)
        - volume: level (0-100)
        - mute: muted (true/false)
        - power: powered (true/false)
        - group: target_player (player ID to join)

        Args:
            player_id: The player ID.
            action: Action to perform.
            position: Seek position in seconds (for seek action).
            level: Volume level 0-100 (for volume action).
            muted: Mute state (for mute action).
            powered: Power state (for power action).
            target_player: Player ID to group with (for group action).
        """
        client = ctx.request_context.lifespan_context["client"]
        result = {"status": "ok", "action": action, "player_id": player_id}

        if action == "play":
            await client.players.play(player_id)
        elif action == "pause":
            await client.players.pause(player_id)
        elif action == "stop":
            await client.players.stop(player_id)
        elif action == "next":
            await client.players.next_track(player_id)
        elif action == "previous":
            await client.players.previous_track(player_id)
        elif action == "seek":
            await client.players.seek(player_id, position)
            result["position"] = position
        elif action == "volume":
            await client.players.volume_set(player_id, level)
            result["level"] = level
        elif action == "mute":
            await client.players.volume_mute(player_id, muted)
            result["muted"] = muted
        elif action == "power":
            await client.players.power(player_id, powered)
            result["powered"] = powered
        elif action == "group":
            await client.players.group(player_id, target_player)
            result["target_player"] = target_player
        elif action == "ungroup":
            await client.players.ungroup(player_id)

        return json.dumps(result)
