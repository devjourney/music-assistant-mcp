"""Music Assistant MCP Server."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiohttp
from fastmcp import FastMCP
from music_assistant_client import MusicAssistantClient
from music_assistant_client.exceptions import CannotConnect, ConnectionFailed

from music_assistant_mcp.connection import MAConnectionConfig

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(mcp: FastMCP) -> AsyncGenerator[dict]:
    """Manage the Music Assistant client lifecycle."""
    config = MAConnectionConfig.from_env()
    session = aiohttp.ClientSession()
    listen_task = None

    try:
        client = MusicAssistantClient(config.server_url, session, token=config.token)

        # start_listening connects and enters the message loop
        ready = asyncio.Event()
        listen_task = asyncio.create_task(client.start_listening(init_ready=ready))
        await ready.wait()

        logger.info("Connected to Music Assistant at %s", config.server_url)
        yield {"client": client}

    except (CannotConnect, ConnectionFailed) as err:
        logger.error("Connection failed: %s", err)
        raise
    finally:
        if listen_task and not listen_task.done():
            listen_task.cancel()
            try:
                await listen_task
            except asyncio.CancelledError:
                pass
        await session.close()


mcp = FastMCP(
    "Music Assistant",
    instructions="Control Music Assistant: search music, manage playback, queues, and playlists.",
    lifespan=lifespan,
)

# Register all tools and resources
from music_assistant_mcp.tools import library, playback, playlists, queue, search  # noqa: E402
from music_assistant_mcp import resources  # noqa: E402

search.register(mcp)
library.register(mcp)
playback.register(mcp)
queue.register(mcp)
playlists.register(mcp)
resources.register(mcp)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
