import json
import os
import tempfile
import unittest
from pathlib import Path

from ota_server import OtaRepository


class OtaRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "manifests" / "test-board").mkdir(parents=True)
        (self.root / "files" / "test-board" / "1.2.3").mkdir(parents=True)
        (self.root / "files" / "test-board" / "1.2.3" / "xiaozhi.bin").write_bytes(
            b"firmware"
        )
        manifest = {
            "firmware": {
                "version": "1.2.3",
                "path": "test-board/1.2.3/xiaozhi.bin",
            }
        }
        (self.root / "manifests" / "test-board" / "stable.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        self.repository = OtaRepository(self.root, "https://example.test/xiaozhi-ota")

    def tearDown(self):
        self.temp.cleanup()

    def test_materializes_versioned_file(self):
        result = self.repository.load("test-board", "stable")
        firmware = result["firmware"]
        self.assertEqual(firmware["version"], "1.2.3")
        self.assertEqual(firmware["size"], 8)
        self.assertEqual(
            firmware["url"],
            "https://example.test/xiaozhi-ota/files/test-board/1.2.3/xiaozhi.bin",
        )
        self.assertEqual(len(firmware["sha256"]), 64)

    def test_board_and_channel_are_isolated(self):
        with self.assertRaises(FileNotFoundError):
            self.repository.load("laoyuanxiaozhi", "stable")
        with self.assertRaises(FileNotFoundError):
            self.repository.load("test-board", "test")

    def test_assets_have_an_independent_version(self):
        asset = self.root / "files/test-board/1.2.3/generated_assets.bin"
        asset.write_bytes(b"new assets")
        path = self.root / "manifests/test-board/stable.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["assets"] = {
            "version": "1.2.1",
            "path": "test-board/1.2.3/generated_assets.bin",
        }
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = self.repository.load("test-board", "stable")
        self.assertEqual(result["firmware"]["version"], "1.2.3")
        self.assertEqual(result["assets"]["version"], "1.2.1")
        self.assertEqual(result["assets"]["size"], 10)

    def test_rejects_unsafe_board(self):
        with self.assertRaises(ValueError):
            self.repository.load("../etc", "stable")

    def test_rejects_file_escape(self):
        outside = self.root / "secret.bin"
        outside.write_bytes(b"not public")
        with self.assertRaises(ValueError):
            self.repository._materialize_section("firmware", {
                "version": "1.2.3", "path": "../secret.bin"
            })


@unittest.skipUnless(os.name == "posix", "Publisher uses Linux flock")
class PublisherTest(unittest.TestCase):
    def test_immutable_release_and_version_validation(self):
        from publish_release import publish
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            stage = root / "stage"
            stage.mkdir()
            data = bytearray(288)
            data[0] = 0xe9
            data[48:53] = b"1.2.3"
            (stage / "xiaozhi.bin").write_bytes(data)
            (stage / "generated_assets.bin").write_bytes(b"assets")
            publish(stage, root / "repo", "test-board", "1.2.3", "test")
            publish(stage, root / "repo", "test-board", "1.2.3", "stable")
            stable = root / "repo/manifests/test-board/stable.json"
            previous = stable.read_bytes()
            (stage / "generated_assets.bin").write_bytes(b"changed")
            with self.assertRaises(ValueError):
                publish(stage, root / "repo", "test-board", "1.2.3", "stable")
            self.assertEqual(stable.read_bytes(), previous)
            with self.assertRaises(ValueError):
                publish(stage, root / "repo", "test-board", "1.2.4", "test")


if __name__ == "__main__":
    unittest.main()
