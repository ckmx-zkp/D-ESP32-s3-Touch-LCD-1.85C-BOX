"""Check a private manifest and hash HTTPS downloads against the local build.

Run with Python 3.10+ and a CA-compatible OpenSSL (Ubuntu is supported).
"""
import argparse
import hashlib
import json
import ssl
import urllib.request
from pathlib import Path
from urllib.parse import urlencode


def verify(board, version, channel, build_directory, ca):
    base = "https://47.108.114.17:9443/xiaozhi-ota/"
    context = ssl.create_default_context(cafile=str(ca))
    request = urllib.request.Request(
        base + "api/v1/check?" + urlencode({"channel": channel}),
        data=json.dumps({"board": {"name": board, "type": board}}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, context=context, timeout=30) as response:
        manifest = json.load(response)
    result = {}
    for section, filename in (("firmware", "xiaozhi.bin"),
                              ("assets", "generated_assets.bin")):
        entry = manifest[section]
        expected = base + "files/" + board + "/" + version + "/" + filename
        if entry["version"] != version or entry["url"] != expected:
            raise ValueError("Unexpected release identity or URL: " + section)
        digest = hashlib.sha256()
        size = 0
        with urllib.request.urlopen(entry["url"], context=context, timeout=60) as response:
            for chunk in iter(lambda: response.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
        local = (Path(build_directory) / filename).read_bytes()
        if (size != entry["size"] or size != len(local) or
                digest.hexdigest() != entry["sha256"] or
                digest.hexdigest() != hashlib.sha256(local).hexdigest()):
            raise ValueError("Downloaded file does not match manifest/local build: " + section)
        result[section] = {"version": version, "size": size,
                           "sha256": digest.hexdigest(), "verified": True}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", default="laoyuanxiaozhi")
    parser.add_argument("--version", required=True)
    parser.add_argument("--channel", choices=("test", "stable"), default="test")
    parser.add_argument("--build-directory", default="build")
    parser.add_argument("--ca", default="deploy/ota-server/ota-root-ca.pem")
    args = parser.parse_args()
    print(json.dumps(verify(args.board, args.version, args.channel,
                            args.build_directory, args.ca), indent=2))
