"""Read-only search diagnostics; run using the cloud MCP virtual environment."""

import asyncio
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import StdioTransport


def emit(kind, **values):
    print(json.dumps({"kind": kind, **values}, ensure_ascii=False), flush=True)


async def main():
    load_dotenv("/etc/xiaozhi-music.env")
    sys.path.insert(0, "/opt/xiaozhi-music")
    import music_gateway

    gateway = music_gateway.Gateway()
    song = "\u8d85\u80fd\u529b"
    artist = "\u9093\u7d2b\u68cb"
    canonical = "G.E.M." + artist
    for query, search_type in [(artist, 100), (song + " " + artist, 1)]:
        form = urllib.parse.urlencode({"s": query, "type": search_type, "offset": 0, "limit": 20})
        data = gateway.request_json(music_gateway.NETEASE_ORIGIN + "/api/search/get/web", form.encode())
        items = data.get("result", {}).get("artists" if search_type == 100 else "songs", [])
        emit("provider_candidates", query=query, search_type=search_type,
             candidates=[{"id": item.get("id"), "name": item.get("name"),
                          "alias": item.get("alias", []),
                          "trans": item.get("trans", []),
                          "artists": [{"id": value.get("id"), "name": value.get("name")}
                                      for value in item.get("artists", item.get("ar", []))]}
                         for item in items[:5]])
    emit("normalized_identity", requested=gateway.normalized(artist),
         canonical=gateway.normalized(canonical),
         equal=gateway.normalized(artist) == gateway.normalized(canonical))

    cases = [(song, artist), (song, ""), (song, canonical), ("", artist),
             (artist + "\u7684" + song, "")]
    for title, singer in cases:
        query = urllib.parse.urlencode({"song": title, "artist": singer})
        request = urllib.request.Request("http://127.0.0.1:3060/stream_pcm?" + query,
                                         headers={"X-Music-Token": os.environ["MUSIC_API_TOKEN"]})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                data = json.load(response)
                emit("gateway_result", song=title, artist=singer, status=response.status,
                     title=data.get("title"), selected_artist=data.get("artist"),
                     has_audio_url=bool(data.get("audio_url")))
        except urllib.error.HTTPError as error:
            emit("gateway_result", song=title, artist=singer, status=error.code,
                 error=json.load(error).get("error"))

    transport = StdioTransport(command=sys.executable,
                               args=["/opt/xiaozhi-music-mcp/music_mcp.py"],
                               env={"MUSIC_API_TOKEN": os.environ["MUSIC_API_TOKEN"],
                                    "MUSIC_GATEWAY_URL": "http://127.0.0.1:3060"})
    async with Client(transport) as client:
        for title, singer in [(song, artist), (song, ""), (song, canonical), ("", artist)]:
            result = await client.call_tool("search_netease_music",
                                            {"song_name": title, "artist_name": singer})
            data = result.data
            if not isinstance(data, dict):
                data = json.loads(result.content[0].text)
            emit("mcp_result", song=title, artist=singer,
                 **{key: data[key] for key in ("success", "title", "artist", "error")
                    if key in data and key != "artist"}, selected_artist=data.get("artist"))


if __name__ == "__main__":
    asyncio.run(main())
