"""Search and browse tools for Music Assistant."""

from __future__ import annotations

import json
from typing import Annotated, Literal

from fastmcp import Context
from music_assistant_models.enums import MediaType
from pydantic import Field

from music_assistant_mcp.serializers import serialize_media_item, serialize_search_results


def register(mcp):
    @mcp.tool()
    async def search_music(
        ctx: Context,
        query: Annotated[str, Field(description="Search query string.")],
        media_types: Annotated[
            list[Literal["track", "album", "artist", "playlist"]] | None,
            Field(description="Types to search for. Defaults to track, album, and artist."),
        ] = None,
        limit: Annotated[int, Field(description="Max results per type (default 10).")] = 10,
    ) -> str:
        """Search for music across all providers."""
        client = ctx.request_context.lifespan_context["client"]
        types = [MediaType(t) for t in (media_types or ["track", "album", "artist"])]
        results = await client.music.search(query, media_types=types, limit=limit)
        return json.dumps(serialize_search_results(results), indent=2)

    @mcp.tool()
    async def browse_media(
        ctx: Context,
        path: Annotated[
            str | None,
            Field(description="Browse path from a previous browse result. Omit for root level."),
        ] = None,
    ) -> str:
        """Browse media providers and folders."""
        client = ctx.request_context.lifespan_context["client"]
        items = await client.music.browse(path)
        return json.dumps([serialize_media_item(i) for i in items], indent=2)

    @mcp.tool()
    async def get_item_by_name(
        ctx: Context,
        name: Annotated[str, Field(description="Name of the item to find.")],
        artist: Annotated[
            str | None, Field(description="Artist name to narrow the search.")
        ] = None,
        album: Annotated[
            str | None, Field(description="Album name to narrow the search.")
        ] = None,
        media_type: Annotated[
            Literal["track", "album", "artist", "playlist"] | None,
            Field(description="Media type to search for."),
        ] = None,
    ) -> str:
        """Find a specific media item by name. Searches library first, then global."""
        client = ctx.request_context.lifespan_context["client"]
        mt = MediaType(media_type) if media_type else None
        item = await client.music.get_item_by_name(name, artist=artist, album=album, media_type=mt)
        if item is None:
            return json.dumps({"error": "Item not found"})
        return json.dumps(serialize_media_item(item), indent=2)
