"""Run with the existing server venv; do not print credentials or signed URLs."""

import asyncio
import json
import os
import sys
import urllib.request

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main():
    load_dotenv("/etc/xiaozhi-music.env")
    transport = StdioTransport(
        command=sys.executable,
        args=["/opt/xiaozhi-music-mcp/music_mcp.py"],
        env={
            "MUSIC_API_TOKEN": os.environ["MUSIC_API_TOKEN"],
            "MUSIC_GATEWAY_URL": "http://127.0.0.1:3060",
        },
    )
    async with Client(transport) as client:
        tools = await client.list_tools()
        assert "search_netease_music" in [tool.name for tool in tools]
        print("MCP_SEARCH_TOOL_OK=1", flush=True)
        result = await client.call_tool(
            "search_netease_music",
            {"song_name": "\u5eb8\u4eba\u81ea\u5a31", "artist_name": "\u80e1\u5927\u5f3a"},
        )
        data = result.data
        if not isinstance(data, dict):
            data = json.loads(result.content[0].text)
        if not data.get("success"):
            print("SEARCH_FAILED=" + str(data.get("error", "unknown")), flush=True)
            raise SystemExit(1)
        print("SEARCH_TITLE=" + data["title"], flush=True)
        print("SEARCH_ARTIST=" + data["artist"], flush=True)
        assert data["title"] == "\u5eb8\u4eba\u81ea\u5a31"
        print("EXACT_TRACK_SEARCH_OK=1", flush=True)
        url = data["audio_url"]
        prefix = "http://47.108.114.17:8081/xiaozhi-music/audio_ogg/"
        assert url.startswith(prefix) and len(url) <= 768
        with urllib.request.urlopen(url, timeout=30) as response:
            audio = response.read(8192)
            assert response.status == 200 and audio.startswith(b"OggS")
            print("OGG_STREAM_OK=1", flush=True)
            print("CONTENT_TYPE=" + response.headers.get("Content-Type", ""), flush=True)
            print("AUDIO_BYTES=" + str(len(audio)), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
