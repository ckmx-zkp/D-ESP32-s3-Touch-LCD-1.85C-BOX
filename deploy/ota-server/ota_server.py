#!/usr/bin/env python3
"""Read-only manifest API for XiaoZhi firmware and assets releases."""

from __future__ import print_function

import hashlib
import json
import logging
import os
import re
import socketserver
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse


LOG = logging.getLogger("xiaozhi-ota")
SAFE_COMPONENT = re.compile(r"^[a-z0-9][a-z0-9.-]{0,95}$")
MAX_REQUEST_BYTES = 256 * 1024
MAX_MANIFEST_BYTES = 64 * 1024


class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


class OtaRepository:
    def __init__(self, root, public_base):
        self.root = Path(root).resolve()
        self.manifests = self.root / "manifests"
        self.files = self.root / "files"
        self.public_base = public_base.rstrip("/")

    @staticmethod
    def _safe_component(value, label):
        if not isinstance(value, str) or not SAFE_COMPONENT.fullmatch(value):
            raise ValueError("invalid {}".format(label))
        return value

    def _manifest_path(self, board, channel):
        board = self._safe_component(board, "board")
        channel = self._safe_component(channel, "channel")
        return self.manifests / board / "{}.json".format(channel)

    def load(self, board, channel):
        path = self._manifest_path(board, channel)
        if not path.is_file():
            raise FileNotFoundError(str(path))
        if path.stat().st_size > MAX_MANIFEST_BYTES:
            raise ValueError("manifest is too large")
        with path.open("r", encoding="utf-8") as stream:
            manifest = json.load(stream)
        if not isinstance(manifest, dict):
            raise ValueError("manifest root must be an object")

        response = {}
        for section_name in ("firmware", "assets"):
            section = manifest.get(section_name)
            if section is None:
                continue
            response[section_name] = self._materialize_section(section_name, section)
        if not response:
            raise ValueError("manifest has no firmware or assets")
        return response

    def _materialize_section(self, section_name, section):
        if not isinstance(section, dict):
            raise ValueError("{} must be an object".format(section_name))
        version = section.get("version")
        relative_path = section.get("path")
        self._safe_component(version, "{} version".format(section_name))
        if not isinstance(relative_path, str) or not relative_path:
            raise ValueError("{} path is missing".format(section_name))

        candidate = (self.files / relative_path).resolve()
        try:
            candidate.relative_to(self.files)
        except ValueError:
            raise ValueError("{} path escapes files root".format(section_name))
        if not candidate.is_file():
            raise FileNotFoundError(str(candidate))

        digest = hashlib.sha256()
        with candidate.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)

        encoded_path = "/".join(quote(part) for part in Path(relative_path).parts)
        result = {
            "version": version,
            "url": "{}/files/{}".format(self.public_base, encoded_path),
            "size": candidate.stat().st_size,
            "sha256": digest.hexdigest(),
        }
        if section.get("force") in (1, True):
            result["force"] = 1
        return result


class OtaHandler(BaseHTTPRequestHandler):
    server_version = "XiaoZhiOTA/1.0"

    def _json_response(self, status, payload):
        data = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/xiaozhi-ota/api/v1/health":
            self._json_response(200, {"status": "ok", "time": int(time.time())})
            return
        self._json_response(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/xiaozhi-ota/api/v1/check":
            self._json_response(404, {"error": "not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json_response(400, {"error": "invalid content length"})
            return
        if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
            self._json_response(413, {"error": "invalid request size"})
            return

        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("request must be an object")
            board_info = payload.get("board", {})
            if not isinstance(board_info, dict):
                raise ValueError("board must be an object")
            board = board_info.get("name") or board_info.get("type")
            channel = parse_qs(parsed.query).get("channel", ["stable"])[0]
            response = self.server.repository.load(board, channel)
        except FileNotFoundError:
            self._json_response(404, {"error": "release not found"})
            return
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as error:
            LOG.warning("Rejected OTA request from %s: %s", self.client_address[0], error)
            self._json_response(400, {"error": str(error)})
            return

        LOG.info("OTA check board=%s channel=%s client=%s", board, channel,
                 self.client_address[0])
        self._json_response(200, response)

    def log_message(self, fmt, *args):
        LOG.info("%s - %s", self.client_address[0], fmt % args)


def main():
    logging.basicConfig(
        level=os.environ.get("OTA_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    host = os.environ.get("OTA_HOST", "127.0.0.1")
    port = int(os.environ.get("OTA_PORT", "3070"))
    root = os.environ.get("OTA_ROOT", "/opt/xiaozhi-ota/data")
    public_base = os.environ.get(
        "OTA_PUBLIC_BASE",
        "https://47.108.114.17:9443/xiaozhi-ota",
    )

    server = ThreadingHTTPServer((host, port), OtaHandler)
    server.repository = OtaRepository(root, public_base)
    LOG.info("Listening on %s:%d, root=%s", host, port, root)
    server.serve_forever()


if __name__ == "__main__":
    main()
