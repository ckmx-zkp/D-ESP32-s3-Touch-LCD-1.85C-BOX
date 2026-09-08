import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image


root = Path(__file__).resolve().parent
sheet = root / "anime-big-head-stickers-20260907-120015-2048x2048.png"
prompt = root.parent / "prompts" / "anime-big-head-stickers.txt"
out = root / "anime-big-head-stickers-individual"
out.mkdir(exist_ok=True)
names = ["happy", "laughing", "surprised", "angry", "tearful", "shy", "thinking", "thumbs-up", "sleepy"]
files = []
with Image.open(sheet) as source:
    width, height = source.size
    for index, name in enumerate(names):
        row, col = divmod(index, 3)
        box = (col * width // 3, row * height // 3,
               (col + 1) * width // 3, (row + 1) * height // 3)
        target = out / f"{index + 1:02d}-{name}.png"
        source.crop(box).save(target)
        files.append(target)

metadata = {
    "metadata_source": "local delivery packaging after relay dimension validation failed",
    "mode": "edit",
    "model": "gpt-image-2",
    "requested_dimensions": [2048, 2048],
    "output_dimensions": [width, height],
    "size_matched": [width, height] == [2048, 2048],
    "upscaled": False,
    "prompt_file": str(prompt),
    "prompt_snapshot": prompt.read_text(encoding="utf-8"),
    "input_image": "C:/Users/98349/AppData/Local/Temp/codex-clipboard-52b5594c-45bf-461b-8eed-d60f6ae10800.jpg",
    "output": str(sheet),
    "individual_dimensions": [width // 3, height // 3],
    "individual_files": [str(path) for path in files],
}
sidecar = sheet.with_suffix(".meta.json")
sidecar.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
archive = root / "anime-big-head-stickers-pack.zip"
with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
    bundle.write(sheet, "sticker-sheet.png")
    bundle.write(sidecar, "generation.meta.json")
    for path in files:
        bundle.write(path, f"stickers/{path.name}")
for path in files:
    with Image.open(path) as sticker:
        sticker.verify()
with ZipFile(archive) as bundle:
    assert bundle.testzip() is None
print(json.dumps({"sheet": str(sheet), "actual_dimensions": [width, height],
                  "size_matched": metadata["size_matched"], "mode": "edit",
                  "sidecar": str(sidecar), "archive": str(archive),
                  "stickers": len(files), "individual_dimensions": metadata["individual_dimensions"]}, indent=2))
