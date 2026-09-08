"""Publish a staged release atomically; published binary files are immutable."""
import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path


def publish(stage, root, board, version, channel):
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{0,95}", board):
        raise ValueError("Invalid board")
    if not re.fullmatch(r"[0-9]{1,8}\.[0-9]{1,8}\.[0-9]{1,8}", version):
        raise ValueError("Invalid version")
    if channel not in ("test", "stable"):
        raise ValueError("Invalid channel")
    stage, root = Path(stage), Path(root)
    firmware = (stage / "xiaozhi.bin").read_bytes()
    if len(firmware) < 288 or firmware[0] != 0xe9:
        raise ValueError("Not a raw ESP application image")
    if firmware[48:80].split(b"\0", 1)[0].decode("ascii") != version:
        raise ValueError("Binary version does not match requested version")
    names = ("xiaozhi.bin", "generated_assets.bin")
    release = root / "files" / board / version
    release.parent.mkdir(parents=True, exist_ok=True)
    manifests = root / "manifests" / board
    manifests.mkdir(parents=True, exist_ok=True)
    with (root / ".publish.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        hashes = {name: hashlib.sha256((stage / name).read_bytes()).hexdigest()
                  for name in names}
        if release.exists():
            for name in names:
                if hashlib.sha256((release / name).read_bytes()).hexdigest() != hashes[name]:
                    raise ValueError("Refusing to overwrite published version")
        else:
            temporary = Path(tempfile.mkdtemp(prefix=".upload-", dir=str(release.parent)))
            for name in names:
                shutil.copyfile(str(stage / name), str(temporary / name))
                os.chmod(str(temporary / name), 0o644)
            os.chmod(str(temporary), 0o755)
            os.rename(str(temporary), str(release))
        manifest = {
            kind: {"version": version, "path": board + "/" + version + "/" + name}
            for kind, name in zip(("firmware", "assets"), names)
        }
        # Keep stable unchanged until the same bytes have been published to test.
        if channel == "stable":
            tested = json.loads((manifests / "test.json").read_text())
            if tested != manifest:
                raise ValueError("Publish this release to test first")
        destination = manifests / (channel + ".json")
        if destination.exists():
            shutil.copyfile(str(destination), str(destination) + ".previous")
        with tempfile.NamedTemporaryFile(mode="w", dir=str(manifests), delete=False) as out:
            json.dump(manifest, out)
            out.flush()
            os.fsync(out.fileno())
            temporary_manifest = out.name
        os.chmod(temporary_manifest, 0o644)
        os.replace(temporary_manifest, str(destination))
        return hashes


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True)
    parser.add_argument("--root", default="/opt/xiaozhi-ota/data")
    parser.add_argument("--board", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--channel", choices=("test", "stable"), default="test")
    args = parser.parse_args()
    print(json.dumps(publish(args.stage, args.root, args.board, args.version, args.channel)))
