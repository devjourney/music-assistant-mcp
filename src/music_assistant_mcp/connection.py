"""Connection configuration for Music Assistant."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class MAConnectionConfig:
    """Music Assistant connection configuration from environment variables."""

    server_url: str
    token: str

    @classmethod
    def from_env(cls) -> MAConnectionConfig:
        """Build connection config from environment variables."""
        server_url = os.environ.get("MA_SERVER_URL")
        if not server_url:
            host = os.environ.get("MA_HOST")
            if not host:
                raise ValueError(
                    "Either MA_SERVER_URL or MA_HOST must be set"
                )
            port = os.environ.get("MA_PORT", "8095")
            server_url = f"http://{host}:{port}"

        token = os.environ.get("MA_TOKEN")
        if not token:
            raise ValueError("MA_TOKEN must be set")

        return cls(
            server_url=server_url.rstrip("/"),
            token=token,
        )
