"""Library browsing tools for Music Assistant."""

from __future__ import annotations

import json
from typing import Literal

from fastmcp import Context
from music_assistant_models.enums import MediaType

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
        media_type: Literal["artist", "album", "track", "playlist"],
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
        favorite: bool | None = None,
        order_by: MediaOrderBy | None = None,
    ) -> str:
        """Browse the music library by media type.

        Args:
            media_type: Type to browse: artist, album, track, or playlist.
            search: Filter by name.
            limit: Max results. Defaults to 25.
            offset: Pagination offset.
            favorite: Filter favorites only (not supported for playlists).
            order_by: Field to sort results by.
        """
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
    async def get_item_children(
        ctx: Context,
        item_id: str,
        provider: str,
        child_type: Literal["album_tracks", "artist_albums", "artist_toptracks", "playlist_tracks"],
    ) -> str:
        """Get child items for a media item.

        Args:
            item_id: The parent item ID.
            provider: Provider instance ID or domain.
            child_type: What to retrieve:
                - album_tracks: tracks on an album
                - artist_albums: albums by an artist
                - artist_toptracks: top tracks for an artist
                - playlist_tracks: tracks in a playlist
        """
        client = ctx.request_context.lifespan_context["client"]
        dispatch = {
            "album_tracks": (client.music.get_album_tracks, serialize_track),
            "artist_albums": (client.music.get_artist_albums, serialize_album),
            "artist_toptracks": (client.music.get_artist_toptracks, serialize_track),
            "playlist_tracks": (client.music.get_playlist_tracks, serialize_track),
        }
        fetch, serialize = dispatch[child_type]
        items = await fetch(item_id, provider)
        return json.dumps([serialize(i) for i in items], indent=2)

    @mcp.tool()
    async def get_similar_tracks(
        ctx: Context,
        item_id: str,
        provider: str,
    ) -> str:
        """Get tracks similar to a given track.

        Args:
            item_id: Track ID.
            provider: Provider instance ID or domain.
        """
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
        limit: int = 10,
        media_types: list[str] | None = None,
    ) -> str:
        """Get recently played items.

        Args:
            limit: Max results. Defaults to 10.
            media_types: Filter by type (track, album, artist, playlist).
        """
        client = ctx.request_context.lifespan_context["client"]
        types = [MediaType(t) for t in media_types] if media_types else None
        items = await client.music.recently_played(limit=limit, media_types=types)
        return json.dumps([serialize_media_item(i) for i in items], indent=2)

    @mcp.tool()
    async def manage_favorites(
        ctx: Context,
        action: Literal["add", "remove"],
        uri: str | None = None,
        media_type: str | None = None,
        item_id: str | None = None,
    ) -> str:
        """Add or remove items from favorites.

        - add: requires uri
        - remove: requires media_type and item_id

        Args:
            action: Action to perform: add or remove.
            uri: URI of the item to favorite (for add).
            media_type: Type of media: track, album, artist, playlist (for remove).
            item_id: The library item ID (for remove).
        """
        client = ctx.request_context.lifespan_context["client"]
        if action == "add":
            await client.music.add_item_to_favorites(uri)
            return json.dumps({"status": "ok", "action": "add_favorite", "uri": uri})
        else:
            await client.music.remove_item_from_favorites(MediaType(media_type), item_id)
            return json.dumps({"status": "ok", "action": "remove_favorite", "media_type": media_type, "item_id": item_id})
