"""Library browsing tools for Music Assistant."""

from __future__ import annotations

import json
from typing import Annotated, Literal

from fastmcp import Context
from music_assistant_models.enums import MediaType
from pydantic import Field

from music_assistant_mcp.serializers import (
    serialize_album,
    serialize_artist,
    serialize_media_item,
    serialize_playlist,
    serialize_track,
)

MediaOrderBy = Literal["name", "sort_name", "timestamp_added", "last_played", "play_count"]


def register(mcp):
    @mcp.tool()
    async def get_library(
        ctx: Context,
        media_type: Annotated[
            Literal["artist", "album", "track", "playlist"],
            Field(description="Type to browse: artist, album, track, or playlist."),
        ],
        search: Annotated[str | None, Field(description="Filter results by name.")] = None,
        limit: Annotated[int, Field(description="Max results (default 25).")] = 25,
        offset: Annotated[int, Field(description="Pagination offset.")] = 0,
        favorite: Annotated[
            bool | None,
            Field(
                description="Filter to favorites only. Applies to artist, album, and track (ignored for playlist)."
            ),
        ] = None,
        order_by: Annotated[
            MediaOrderBy | None, Field(description="Sort results by this field.")
        ] = None,
    ) -> str:
        """Browse the music library by media type."""
        client = ctx.request_context.lifespan_context["client"]
        serializers = {
            "artist": (client.music.get_library_artists, serialize_artist),
            "album": (client.music.get_library_albums, serialize_album),
            "track": (client.music.get_library_tracks, serialize_track),
            "playlist": (client.music.get_library_playlists, serialize_playlist),
        }
        fetch, serialize = serializers[media_type]
        kwargs = {"search": search, "limit": limit, "offset": offset, "order_by": order_by}
        if media_type != "playlist":
            kwargs["favorite"] = favorite
        items = await fetch(**kwargs)
        return json.dumps([serialize(i) for i in items], indent=2)

    @mcp.tool()
    async def get_album_tracks(
        ctx: Context,
        item_id: Annotated[str, Field(description="The album ID.")],
        provider: Annotated[str, Field(description="Provider instance ID or domain.")],
    ) -> str:
        """Get all tracks on an album."""
        client = ctx.request_context.lifespan_context["client"]
        tracks = await client.music.get_album_tracks(item_id, provider)
        return json.dumps([serialize_track(t) for t in tracks], indent=2)

    @mcp.tool()
    async def get_artist_details(
        ctx: Context,
        item_id: Annotated[str, Field(description="The artist ID.")],
        provider: Annotated[str, Field(description="Provider instance ID or domain.")],
        detail_type: Annotated[
            Literal["albums", "top_tracks"],
            Field(description="What to retrieve: albums or top_tracks."),
        ],
    ) -> str:
        """Get albums or top tracks for an artist."""
        client = ctx.request_context.lifespan_context["client"]
        dispatch = {
            "albums": (client.music.get_artist_albums, serialize_album),
            "top_tracks": (client.music.get_artist_toptracks, serialize_track),
        }
        fetch, serialize = dispatch[detail_type]
        items = await fetch(item_id, provider)
        return json.dumps([serialize(i) for i in items], indent=2)

    @mcp.tool()
    async def get_similar_tracks(
        ctx: Context,
        item_id: Annotated[str, Field(description="The track ID.")],
        provider: Annotated[str, Field(description="Provider instance ID or domain.")],
    ) -> str:
        """Get tracks similar to a given track."""
        client = ctx.request_context.lifespan_context["client"]
        tracks = await client.music.similar_tracks(item_id, provider)
        return json.dumps([serialize_track(t) for t in tracks], indent=2)

    @mcp.tool()
    async def get_recommendations(ctx: Context) -> str:
        """Get personalized music recommendations."""
        client = ctx.request_context.lifespan_context["client"]
        folders = await client.music.recommendations()
        result = []
        for folder in folders:
            entry = {
                "name": folder.name,
                "subtitle": getattr(folder, "subtitle", None),
                "items": [serialize_media_item(i) for i in folder.items],
            }
            result.append(entry)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_recently_played(
        ctx: Context,
        limit: Annotated[int, Field(description="Max results (default 10).")] = 10,
        media_types: Annotated[
            list[Literal["track", "album", "artist", "playlist"]] | None,
            Field(description="Filter by media type. Returns all types if not specified."),
        ] = None,
    ) -> str:
        """Get recently played items."""
        client = ctx.request_context.lifespan_context["client"]
        types = [MediaType(t) for t in media_types] if media_types else None
        items = await client.music.recently_played(limit=limit, media_types=types)
        return json.dumps([serialize_media_item(i) for i in items], indent=2)

    @mcp.tool()
    async def manage_favorites(
        ctx: Context,
        action: Annotated[
            Literal["add", "remove"],
            Field(description="Action to perform: add or remove."),
        ],
        uri: Annotated[
            str | None,
            Field(description="URI of the item to favorite (required for add)."),
        ] = None,
        media_type: Annotated[
            Literal["track", "album", "artist", "playlist"] | None,
            Field(description="Media type (required for remove)."),
        ] = None,
        item_id: Annotated[
            str | None,
            Field(description="The library item ID (required for remove)."),
        ] = None,
    ) -> str:
        """Add or remove items from favorites."""
        client = ctx.request_context.lifespan_context["client"]
        if action == "add":
            await client.music.add_item_to_favorites(uri)
            return json.dumps({"status": "ok", "action": "add_favorite", "uri": uri})
        else:
            await client.music.remove_item_from_favorites(MediaType(media_type), item_id)
            return json.dumps({"status": "ok", "action": "remove_favorite", "media_type": media_type, "item_id": item_id})
