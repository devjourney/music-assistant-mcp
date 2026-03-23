"""Playlist management tools for Music Assistant."""

from __future__ import annotations

import json
from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from music_assistant_mcp.serializers import serialize_playlist, serialize_track


def register(mcp):
    @mcp.tool()
    async def create_playlist(
        ctx: Context,
        name: Annotated[str, Field(description="Name for the new playlist.")],
        provider: Annotated[
            str | None,
            Field(description="Provider instance ID or domain. Uses default if not specified."),
        ] = None,
    ) -> str:
        """Create a new playlist."""
        client = ctx.request_context.lifespan_context["client"]
        playlist = await client.music.create_playlist(name, provider_instance_or_domain=provider)
        return json.dumps(serialize_playlist(playlist), indent=2)

    @mcp.tool()
    async def manage_playlist_tracks(
        ctx: Context,
        playlist_id: Annotated[str, Field(description="The playlist ID (database ID).")],
        action: Annotated[
            Literal["list", "add", "remove"],
            Field(description="Action to perform: list, add, or remove."),
        ],
        uris: Annotated[
            list[str] | None,
            Field(description="Track URIs to add (required for add action)."),
        ] = None,
        positions: Annotated[
            list[int] | None,
            Field(description="0-indexed track positions to remove (required for remove action)."),
        ] = None,
    ) -> str:
        """List, add, or remove tracks from a playlist."""
        client = ctx.request_context.lifespan_context["client"]
        if action == "list":
            tracks = await client.music.get_playlist_tracks(playlist_id)
            return json.dumps([serialize_track(t) for t in tracks], indent=2)
        elif action == "add":
            await client.music.add_playlist_tracks(playlist_id, uris)
            return json.dumps({"status": "ok", "action": "add_tracks", "playlist_id": playlist_id, "count": len(uris)})
        else:
            await client.music.remove_playlist_tracks(playlist_id, tuple(positions))
            return json.dumps({"status": "ok", "action": "remove_tracks", "playlist_id": playlist_id, "count": len(positions)})
