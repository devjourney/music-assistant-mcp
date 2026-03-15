"""Search and browse tools for Music Assistant."""

from __future__ import annotations

import json

from fastmcp import Context
from music_assistant_models.enums import MediaType

from music_assistant_mcp.serializers import serialize_media_item, serialize_search_results


def register(mcp):
    @mcp.tool()
    async def search_music(
        ctx: Context,
        query: str,
        media_types: list[str] | None = None,
        limit: int = 10,
    ) -> str:
        """Search for music across all providers.

        Args:
            query: Search query string.
            media_types: Types to search for (track, album, artist, playlist). Defaults to track, album, artist.
            limit: Max results per type. Defaults to 10.
        """
        client = ctx.request_context.lifespan_context["client"]
        types = [MediaType(t) for t in (media_types or ["track", "album", "artist"])]
        results = await client.music.search(query, media_types=types, limit=limit)
        return json.dumps(serialize_search_results(results), indent=2)

    @mcp.tool()
    async def browse_media(ctx: Context, path: str | None = None) -> str:
        """Browse media providers and folders.

        Args:
            path: Browse path. None for root level.
        """
        client = ctx.request_context.lifespan_context["client"]
        items = await client.music.browse(path)
        return json.dumps([serialize_media_item(i) for i in items], indent=2)

    @mcp.tool()
    async def get_item_by_name(
        ctx: Context,
        name: str,
        artist: str | None = None,
        album: str | None = None,
        media_type: str | None = None,
    ) -> str:
        """Find a specific media item by name. Searches library first, then global.

        Args:
            name: Name of the item to find.
            artist: Artist name to narrow the search.
            album: Album name to narrow the search.
            media_type: One of: track, album, artist, playlist.
        """
        client = ctx.request_context.lifespan_context["client"]
        mt = MediaType(media_type) if media_type else None
        item = await client.music.get_item_by_name(name, artist=artist, album=album, media_type=mt)
        if item is None:
            return json.dumps({"error": "Item not found"})
        return json.dumps(serialize_media_item(item), indent=2)
