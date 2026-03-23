"""Queue management tools for Music Assistant."""

from __future__ import annotations

import json
from typing import Annotated, Literal

from fastmcp import Context
from music_assistant_models.enums import QueueOption, RepeatMode
from pydantic import Field

from music_assistant_mcp.serializers import serialize_queue, serialize_queue_item


def register(mcp):
    @mcp.tool()
    async def play_media(
        ctx: Context,
        queue_id: Annotated[str, Field(description="The queue/player ID.")],
        media: Annotated[
            str | list[str], Field(description="URI string or list of URI strings to play.")
        ],
        option: Annotated[
            Literal["play", "replace", "next", "replace_next", "add"],
            Field(description="How to queue the media."),
        ] = "play",
        radio_mode: Annotated[
            bool, Field(description="Keep playing similar tracks after the queue ends.")
        ] = False,
    ) -> str:
        """Play media on a queue."""
        client = ctx.request_context.lifespan_context["client"]
        queue_option = QueueOption(option.lower()) if option else None
        await client.player_queues.play_media(
            queue_id, media=media, option=queue_option, radio_mode=radio_mode
        )
        return json.dumps({"status": "ok", "action": "play_media", "queue_id": queue_id})

    @mcp.tool()
    async def get_queue(
        ctx: Context,
        queue_id: Annotated[str, Field(description="The queue/player ID.")],
    ) -> str:
        """Get the current state of a player queue."""
        client = ctx.request_context.lifespan_context["client"]
        queue = client.player_queues.get(queue_id)
        if queue is None:
            return json.dumps({"error": f"Queue {queue_id} not found"})
        return json.dumps(serialize_queue(queue), indent=2)

    @mcp.tool()
    async def get_queue_items(
        ctx: Context,
        queue_id: Annotated[str, Field(description="The queue/player ID.")],
        limit: Annotated[int, Field(description="Max items to return (default 25).")] = 25,
        offset: Annotated[int, Field(description="Pagination offset.")] = 0,
    ) -> str:
        """Get items in a player queue."""
        client = ctx.request_context.lifespan_context["client"]
        items = await client.player_queues.get_queue_items(queue_id, limit=limit, offset=offset)
        return json.dumps([serialize_queue_item(i) for i in items], indent=2)

    @mcp.tool()
    async def queue_control(
        ctx: Context,
        queue_id: Annotated[str, Field(description="The queue/player ID.")],
        action: Annotated[
            Literal["clear", "shuffle", "repeat"],
            Field(description="Action to perform."),
        ],
        enabled: Annotated[
            bool | None, Field(description="Enable/disable (for shuffle action).")
        ] = None,
        mode: Annotated[
            Literal["off", "one", "all"] | None,
            Field(description="Repeat mode (for repeat action)."),
        ] = None,
    ) -> str:
        """Control queue settings."""
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
