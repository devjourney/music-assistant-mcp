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
