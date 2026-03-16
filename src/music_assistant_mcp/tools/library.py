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
    async def get_library_artists(
        ctx: Context,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
        favorite: bool | None = None,
        order_by: MediaOrderBy | None = None,
    ) -> str:
        """Get artists from the library.

        Args:
            search: Filter by name.
            limit: Max results. Defaults to 25.
            offset: Pagination offset.
            favorite: Filter favorites only.
            order_by: Field to sort results by.
        """
        client = ctx.request_context.lifespan_context["client"]
        artists = await client.music.get_library_artists(
            favorite=favorite, search=search, limit=limit, offset=offset,
            order_by=order_by,
        )
        return json.dumps([serialize_artist(a) for a in artists], indent=2)

    @mcp.tool()
    async def get_library_albums(
        ctx: Context,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
        favorite: bool | None = None,
        order_by: MediaOrderBy | None = None,
    ) -> str:
        """Get albums from the library.

        Args:
            search: Filter by name.
            limit: Max results. Defaults to 25.
            offset: Pagination offset.
            favorite: Filter favorites only.
            order_by: Field to sort results by.
        """
        client = ctx.request_context.lifespan_context["client"]
        albums = await client.music.get_library_albums(
            favorite=favorite, search=search, limit=limit, offset=offset,
            order_by=order_by,
        )
        return json.dumps([serialize_album(a) for a in albums], indent=2)

    @mcp.tool()
    async def get_library_tracks(
        ctx: Context,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
        favorite: bool | None = None,
        order_by: MediaOrderBy | None = None,
    ) -> str:
        """Get tracks from the library.

        Args:
            search: Filter by name.
            limit: Max results. Defaults to 25.
            offset: Pagination offset.
            favorite: Filter favorites only.
            order_by: Field to sort results by.
        """
        client = ctx.request_context.lifespan_context["client"]
        tracks = await client.music.get_library_tracks(
            favorite=favorite, search=search, limit=limit, offset=offset,
            order_by=order_by,
        )
        return json.dumps([serialize_track(t) for t in tracks], indent=2)

    @mcp.tool()
    async def get_library_playlists(
        ctx: Context,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
        order_by: MediaOrderBy | None = None,
    ) -> str:
        """Get playlists from the library.

        Args:
            search: Filter by name.
            limit: Max results. Defaults to 25.
            offset: Pagination offset.
            order_by: Field to sort results by.
        """
        client = ctx.request_context.lifespan_context["client"]
        playlists = await client.music.get_library_playlists(
            search=search, limit=limit, offset=offset,
            order_by=order_by,
        )
        return json.dumps([serialize_playlist(p) for p in playlists], indent=2)

    @mcp.tool()
    async def get_album_tracks(
        ctx: Context,
        item_id: str,
        provider: str,
    ) -> str:
        """Get all tracks on an album.

        Args:
            item_id: Album ID.
            provider: Provider instance ID or domain.
        """
        client = ctx.request_context.lifespan_context["client"]
        tracks = await client.music.get_album_tracks(item_id, provider)
        return json.dumps([serialize_track(t) for t in tracks], indent=2)

    @mcp.tool()
    async def get_artist_albums(
        ctx: Context,
        item_id: str,
        provider: str,
    ) -> str:
        """Get all albums by an artist.

        Args:
            item_id: Artist ID.
            provider: Provider instance ID or domain.
        """
        client = ctx.request_context.lifespan_context["client"]
        albums = await client.music.get_artist_albums(item_id, provider)
        return json.dumps([serialize_album(a) for a in albums], indent=2)

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
    async def get_artist_toptracks(
        ctx: Context,
        item_id: str,
        provider: str,
    ) -> str:
        """Get top tracks for an artist.

        Args:
            item_id: Artist ID.
            provider: Provider instance ID or domain.
        """
        client = ctx.request_context.lifespan_context["client"]
        tracks = await client.music.get_artist_toptracks(item_id, provider)
        return json.dumps([serialize_track(t) for t in tracks], indent=2)

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
    async def add_to_favorites(
        ctx: Context,
        uri: str,
    ) -> str:
        """Add a media item to favorites.

        Args:
            uri: The URI of the item to favorite.
        """
        client = ctx.request_context.lifespan_context["client"]
        await client.music.add_item_to_favorites(uri)
        return json.dumps({"status": "ok", "action": "add_favorite", "uri": uri})

    @mcp.tool()
    async def remove_from_favorites(
        ctx: Context,
        media_type: str,
        item_id: str,
    ) -> str:
        """Remove an item from favorites.

        Args:
            media_type: Type of media (track, album, artist, playlist).
            item_id: The library item ID.
        """
        client = ctx.request_context.lifespan_context["client"]
        await client.music.remove_item_from_favorites(MediaType(media_type), item_id)
        return json.dumps({"status": "ok", "action": "remove_favorite", "media_type": media_type, "item_id": item_id})
