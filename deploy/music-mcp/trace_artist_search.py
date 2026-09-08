"""Trace provider response codes and chosen artist IDs without exposing credentials."""

import json
import sys
import urllib.parse

from dotenv import load_dotenv


load_dotenv("/etc/xiaozhi-music.env")
sys.path.insert(0, "/opt/xiaozhi-music")
import music_gateway

gateway = music_gateway.Gateway()
request_json = gateway.request_json


def trace(url, data=None):
    payload = request_json(url, data)
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(data.decode() if data else parsed.query)
    result = payload.get("result") or {}
    artists = result.get("artists", [])
    songs = payload.get("songs", result.get("songs", []))
    print(json.dumps({"kind": "provider_trace", "path": parsed.path, "query": query,
                      "code": payload.get("code"), "message": payload.get("message"),
                      "keys": list(payload), "artist_count": len(artists),
                      "song_count": len(songs), "more": payload.get("more"),
                      "artists": [{"id": item.get("id"), "name": item.get("name"),
                                   "alias": item.get("alias", [])} for item in artists[:3]],
                      "exact_songs": [{"id": item.get("id"), "name": item.get("name")}
                                      for item in songs if item.get("name") == "\u8d85\u80fd\u529b"]},
                     ensure_ascii=False), flush=True)
    return payload


gateway.request_json = trace
for singer in ["\u9093\u7d2b\u68cb", "G.E.M.\u9093\u7d2b\u68cb"]:
    print(json.dumps({"kind": "case", "artist": singer}, ensure_ascii=False), flush=True)
    try:
        selected = gateway.search("\u8d85\u80fd\u529b", singer)
        print(json.dumps({"kind": "selected", "id": selected["id"],
                          "title": selected["name"]}, ensure_ascii=False), flush=True)
    except LookupError as error:
        print(json.dumps({"kind": "not_found", "error": str(error)}, ensure_ascii=False), flush=True)
