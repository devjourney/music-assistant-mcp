"""Serializers to convert Music Assistant model objects to JSON-friendly dicts."""

from __future__ import annotations

from typing import Any


def serialize_artist(artist: Any) -> dict[str, Any]:
    return {
        "item_id": artist.item_id,
        "provider": artist.provider,
        "name": artist.name,
        "uri": artist.uri,
        "favorite": getattr(artist, "favorite", None),
    }


def serialize_album(album: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "item_id": album.item_id,
        "provider": album.provider,
        "name": album.name,
        "uri": album.uri,
    }
    if hasattr(album, "artists") and album.artists:
        result["artists"] = [
            {"name": a.name, "item_id": getattr(a, "item_id", None)}
            for a in album.artists
        ]
    if hasattr(album, "year") and album.year:
        result["year"] = album.year
    if hasattr(album, "album_type"):
        result["album_type"] = str(album.album_type)
    if hasattr(album, "favorite"):
        result["favorite"] = album.favorite
    return result


def serialize_track(track: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "item_id": track.item_id,
        "provider": track.provider,
        "name": track.name,
        "uri": track.uri,
        "duration": getattr(track, "duration", None),
        "favorite": getattr(track, "favorite", None),
    }
    if hasattr(track, "artists") and track.artists:
        result["artists"] = [
            {"name": a.name, "item_id": getattr(a, "item_id", None)}
            for a in track.artists
        ]
    if hasattr(track, "album") and track.album:
        result["album"] = {
            "name": track.album.name,
            "item_id": getattr(track.album, "item_id", None),
        }
    if hasattr(track, "track_number") and track.track_number:
        result["track_number"] = track.track_number
    if hasattr(track, "disc_number") and track.disc_number:
        result["disc_number"] = track.disc_number
    return result


def serialize_playlist(playlist: Any) -> dict[str, Any]:
    return {
        "item_id": playlist.item_id,
        "provider": playlist.provider,
        "name": playlist.name,
        "uri": playlist.uri,
        "owner": getattr(playlist, "owner", None),
        "is_editable": getattr(playlist, "is_editable", None),
    }


def serialize_player(player: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "player_id": player.player_id,
        "name": player.name,
        "available": player.available,
        "powered": player.powered,
        "state": str(player.playback_state) if player.playback_state else None,
        "volume_level": player.volume_level,
        "type": str(player.type) if hasattr(player, "type") else None,
    }
    if player.current_media:
        cm = player.current_media
        result["current_media"] = {
            "title": getattr(cm, "title", None),
            "artist": getattr(cm, "artist", None),
            "album": getattr(cm, "album", None),
            "uri": getattr(cm, "uri", None),
        }
    return result


def serialize_queue(queue: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "queue_id": queue.queue_id,
        "display_name": getattr(queue, "display_name", None),
        "active": queue.active,
        "state": str(queue.state) if queue.state else None,
        "shuffle_enabled": queue.shuffle_enabled,
        "repeat_mode": str(queue.repeat_mode) if queue.repeat_mode else None,
        "current_index": queue.current_index,
        "items": queue.items,
        "elapsed_time": queue.elapsed_time,
    }
    if queue.current_item:
        result["current_item"] = serialize_queue_item(queue.current_item)
    if queue.next_item:
        result["next_item"] = serialize_queue_item(queue.next_item)
    return result


def serialize_queue_item(item: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "queue_item_id": item.queue_item_id,
        "name": item.name,
        "duration": item.duration,
        "index": item.index,
    }
    if item.media_item:
        result["media_item"] = serialize_media_item(item.media_item)
    return result


def serialize_media_item(item: Any) -> dict[str, Any]:
    """Serialize any media item by dispatching to the appropriate serializer."""
    from music_assistant_models.enums import MediaType

    media_type = getattr(item, "media_type", None)
    if media_type == MediaType.TRACK:
        return serialize_track(item)
    elif media_type == MediaType.ALBUM:
        return serialize_album(item)
    elif media_type == MediaType.ARTIST:
        return serialize_artist(item)
    elif media_type == MediaType.PLAYLIST:
        return serialize_playlist(item)
    # Fallback for ItemMapping or unknown types
    return {
        "item_id": getattr(item, "item_id", None),
        "provider": getattr(item, "provider", None),
        "name": getattr(item, "name", None),
        "uri": getattr(item, "uri", None),
        "media_type": str(media_type) if media_type else None,
    }


def serialize_search_results(results: Any) -> dict[str, Any]:
    output: dict[str, Any] = {}
    if results.artists:
        output["artists"] = [serialize_media_item(a) for a in results.artists]
    if results.albums:
        output["albums"] = [serialize_media_item(a) for a in results.albums]
    if results.tracks:
        output["tracks"] = [serialize_media_item(t) for t in results.tracks]
    if results.playlists:
        output["playlists"] = [serialize_media_item(p) for p in results.playlists]
    if results.radio:
        output["radio"] = [serialize_media_item(r) for r in results.radio]
    return output
