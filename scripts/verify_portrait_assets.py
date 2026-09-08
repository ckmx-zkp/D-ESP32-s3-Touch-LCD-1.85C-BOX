"""Verify the actual flash asset image against the reviewed portrait manifest."""

import hashlib
import io
import json
import struct
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "main/boards/waveshare/esp32-s3-touch-lcd-1.85c/assets"


def main():
    packed = (ROOT / "build/generated_assets.bin").read_bytes()
    count, checksum, data_length = struct.unpack_from("<III", packed)
    assert data_length == len(packed) - 12
    assert sum(packed[12:]) & 0xFFFF == checksum
    assert len(packed) < 8 * 1024 * 1024
    entry = struct.Struct("<32sIIHH")
    start = 12 + count * entry.size
    files = {}
    for index in range(count):
        name, size, offset, _, _ = entry.unpack_from(packed, 12 + index * entry.size)
        name = name.split(b"\0", 1)[0].decode("utf-8")
        position = start + offset
        assert position + 2 + size <= len(packed)
        assert packed[position:position + 2] == b"ZZ"
        assert name not in files
        files[name] = packed[position + 2:position + 2 + size]
    manifest = json.loads((ASSETS / "portrait-manifest.json").read_text(encoding="utf-8"))
    index = json.loads(files["index.json"])
    emotions = {item["name"]: item["file"] for item in index["emoji_collection"]}
    expected = {item["name"] for item in manifest["expressions"]}
    assert len(emotions) == len(index["emoji_collection"]) == len(expected) == 21
    assert set(emotions) == expected
    for item in manifest["expressions"]:
        content = files[emotions[item["name"]]]
        assert hashlib.sha256(content).hexdigest() == item["sha256"], item["name"]
        assert content == (ROOT / item["file"]).read_bytes(), item["name"]
        with Image.open(io.BytesIO(content)) as picture:
            assert picture.size == (360, 360)
            picture.verify()
    assert index["srmodels"] in files
    assert index["text_font"] in files
    result = {
        "result": "PASS", "portrait_count": len(emotions), "portrait_size": [360, 360],
        "assets_bytes": len(packed), "partition_bytes": 8 * 1024 * 1024,
        "assets_sha256": hashlib.sha256(packed).hexdigest(),
        "wake_word_models": index["srmodels"], "text_font": index["text_font"],
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
