"""Crop the approved portrait sheets into the BOX V2's 360x360 PNG collection."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "main/boards/waveshare/esp32-s3-touch-lcd-1.85c/assets/emoji"
SHEETS = {
    "a": ["happy", "laughing", "surprised", "angry", "crying", "embarrassed",
          "thinking", "confident", "sleepy"],
    "b": ["neutral", "sad", "shocked", "confused", "cool", "winking", "loving",
          "kissy", "relaxed"],
    "c": ["funny", "silly", "delicious"],
}


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []
    previews = []
    for part, names in SHEETS.items():
        requested = (3072, 1024) if part == "c" else (2048, 2048)
        source = ROOT / "generated" / (
            f"portrait-firmware-{part}-20260907-123300-{requested[0]}x{requested[1]}.png"
        )
        with Image.open(source) as opened:
            sheet = opened.convert("RGB")
        rows = len(names) // 3
        # Sheet B's generated row gutters are offset from an exact mathematical grid.
        row_edges = [0, 410, 810, sheet.height] if part == "b" else [
            row * sheet.height // rows for row in range(rows + 1)
        ]
        for index, name in enumerate(names):
            row, col = divmod(index, 3)
            cell = sheet.crop((col * sheet.width // 3, row_edges[row],
                               (col + 1) * sheet.width // 3, row_edges[row + 1]))
            # Ignore faint background texture while retaining the drawn face and accents.
            mask = ImageChops.difference(cell, Image.new("RGB", cell.size, "white"))
            bounds = mask.convert("L").point(lambda value: 255 if value > 32 else 0).getbbox()
            if bounds is None:
                raise ValueError(f"Blank expression: {name}")
            left, top, right, bottom = bounds
            crop = cell.crop((max(0, left - 2), max(0, top - 2),
                              min(cell.width, right + 2), min(cell.height, bottom + 2)))
            if crop.height < 316 or crop.width < 180:
                raise ValueError(f"Source resolution too small: {name} {crop.size}")
            portrait = ImageOps.contain(crop, (328, 316), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (360, 360), "white")
            canvas.paste(portrait, ((360 - portrait.width) // 2, 32))
            target = OUTPUT / f"{name}.png"
            canvas.save(target, optimize=True)
            with Image.open(target) as verified:
                assert verified.size == (360, 360)
                verified.verify()
            records.append({"name": name, "file": str(target.relative_to(ROOT)),
                            "source": source.name, "source_cell": index,
                            "dimensions": [360, 360],
                            "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
            circle = Image.new("L", (360, 360))
            ImageDraw.Draw(circle).ellipse((0, 0, 359, 359), fill=255)
            tile = Image.new("RGB", (376, 398), "#e6e9ed")
            tile.paste(canvas, (8, 8), circle)
            ImageDraw.Draw(tile).text((16, 378), name, fill="#24272b")
            previews.append(tile)
        prompt = ROOT / "prompts" / f"portrait-firmware-{part}.txt"
        metadata = {
            "metadata_source": "local validation after relay requested-size mismatch",
            "mode": "edit", "model": "gpt-image-2",
            "requested_dimensions": requested, "output_dimensions": sheet.size,
            "size_matched": requested == sheet.size, "upscaled": False,
            "prompt_file": str(prompt.relative_to(ROOT)),
            "prompt_snapshot": prompt.read_text(encoding="utf-8"),
            "output": str(source.relative_to(ROOT)), "expressions": names,
        }
        source.with_suffix(".meta.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
    assert len(records) == 21
    original = ROOT / "managed_components/78__xiaozhi-fonts/png/noto-color-emoji_64"
    assert {item["name"] for item in records} == {path.stem for path in original.glob("*.png")}
    assert {path.stem for path in OUTPUT.glob("*.png")} == {item["name"] for item in records}
    contact = Image.new("RGB", (376 * 7, 398 * 3), "#e6e9ed")
    for index, tile in enumerate(previews):
        contact.paste(tile, ((index % 7) * 376, (index // 7) * 398))
    contact.save(ROOT / "generated/portrait-firmware-round-preview.png")
    (OUTPUT.parent / "portrait-manifest.json").write_text(
        json.dumps({"dimensions": [360, 360], "expressions": records}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Verified {len(records)} / 21 standard emotions, all 360x360 RGB PNGs.")
    print(f"PNG bytes: {sum(path.stat().st_size for path in OUTPUT.glob('*.png'))}")


if __name__ == "__main__":
    main()
