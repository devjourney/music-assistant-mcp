# MusicAssistantMCP

MCP server wrapping `music-assistant-client` via FastMCP.

## Project Structure

- `src/music_assistant_mcp/server.py` - FastMCP instance, lifespan, entry point
- `src/music_assistant_mcp/connection.py` - Env var parsing, auth config
- `src/music_assistant_mcp/serializers.py` - MA model → dict converters
- `src/music_assistant_mcp/tools/` - Tool modules (search, library, playback, queue, playlists)
- `src/music_assistant_mcp/resources.py` - MCP resources

## Key Patterns

- Each tool module has a `register(mcp)` function that decorates tools onto the FastMCP instance
- Tools get the MA client from `ctx.request_context.lifespan_context["client"]`
- All tools return JSON strings
- The lifespan context manager handles connection/auth lifecycle
- Serializers use `getattr` with fallbacks to handle both full model objects and `ItemMapping` lightweight refs

## Running

```bash
MA_SERVER_URL=http://host:8095 MA_TOKEN=xxx music-assistant-mcp
```
