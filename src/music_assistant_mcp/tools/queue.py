"""Queue management tools for Music Assistant."""

from __future__ import annotations

import json
from typing import Literal

from fastmcp import Context
from music_assistant_models.enums import QueueOption, RepeatMode

from music_assistant_mcp.serializers import serialize_queue, serialize_queue_item


def register(mcp):
    @mcp.tool()
    async def play_media(
        ctx: Context,
        queue_id: str,
        media: str | list[str],
        option: str = "play",
        radio_mode: bool = False,
    ) -> str:
        """Play media on a queue. Media can be URIs or item names.

        Args:
            queue_id: The queue/player ID.
            media: URI string or list of URI strings to play.
            option: Queue option: play, replace, next, replace_next, add. Defaults to play.
            radio_mode: Enable radio mode to keep playing similar tracks. Defaults to False.
        """
        client = ctx.request_context.lifespan_context["client"]
        queue_option = QueueOption(option.lower()) if option else None
        await client.player_queues.play_media(
            queue_id, media=media, option=queue_option, radio_mode=radio_mode
        )
        return json.dumps({"status": "ok", "action": "play_media", "queue_id": queue_id})

    @mcp.tool()
    async def get_queue(ctx: Context, queue_id: str) -> str:
        """Get the current state of a player queue.

        Args:
            queue_id: The queue/player ID.
        """
        client = ctx.request_context.lifespan_context["client"]
        queue = client.player_queues.get(queue_id)
        if queue is None:
            return json.dumps({"error": f"Queue {queue_id} not found"})
        return json.dumps(serialize_queue(queue), indent=2)

    @mcp.tool()
    async def get_queue_items(
        ctx: Context,
        queue_id: str,
        limit: int = 25,
        offset: int = 0,
    ) -> str:
        """Get items in a player queue.

        Args:
            queue_id: The queue/player ID.
            limit: Max items to return. Defaults to 25.
            offset: Pagination offset.
        """
        client = ctx.request_context.lifespan_context["client"]
        items = await client.player_queues.get_queue_items(queue_id, limit=limit, offset=offset)
        return json.dumps([serialize_queue_item(i) for i in items], indent=2)

    @mcp.tool()
    async def queue_control(
        ctx: Context,
        queue_id: str,
        action: Literal["clear", "shuffle", "repeat"],
        enabled: bool | None = None,
        mode: str | None = None,
    ) -> str:
        """Control queue settings.

        - clear: clear all items from the queue
        - shuffle: enable or disable shuffle (requires enabled param)
        - repeat: set repeat mode (requires mode param: off, one, or all)

        Args:
            queue_id: The queue/player ID.
            action: Action to perform: clear, shuffle, or repeat.
            enabled: Shuffle state (for shuffle action).
            mode: Repeat mode: off, one, or all (for repeat action).
        """
        client = ctx.request_context.lifespan_context["client"]
        result = {"status": "ok", "action": action, "queue_id": queue_id}

        if action == "clear":
            await client.player_queues.clear(queue_id)
        elif action == "shuffle":
            await client.player_queues.shuffle(queue_id, enabled)
            result["enabled"] = enabled
        elif action == "repeat":
            repeat_mode = RepeatMode(mode.lower())
            await client.player_queues.repeat(queue_id, repeat_mode)
            result["mode"] = mode

        return json.dumps(result)
