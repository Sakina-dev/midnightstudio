"""Compress portfolio PNGs and generate WebP variants."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
WEBP_QUALITY = 82


def max_width_for(rel: str) -> int:
    rel = rel.replace("\\", "/")
    if "midnight_logo" in rel:
        return 640
    if "backgroundblue" in rel:
        return 1920
    if rel.startswith("carte/"):
        return 960
    if "flyer" in rel:
        return 2400
    if "post" in rel:
        return 1800
    if "chartegraphique" in rel:
        return 2000
    return 1680


def prepare_image(im: Image.Image) -> Image.Image:
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        return im.convert("RGBA")
    if im.mode != "RGB":
        return im.convert("RGB")
    return im


def resize_if_needed(im: Image.Image, max_w: int) -> Image.Image:
    w, h = im.size
    if w <= max_w:
        return im
    ratio = max_w / w
    return im.resize((max_w, int(h * ratio)), Image.Resampling.LANCZOS)


def process(path: Path) -> tuple[int, int, int]:
    rel = str(path.relative_to(ROOT))
    orig_bytes = path.stat().st_size
    max_w = max_width_for(rel)

    with Image.open(path) as source:
        im = resize_if_needed(prepare_image(source), max_w)
        webp_path = path.with_suffix(".webp")
        im.save(webp_path, "WEBP", quality=WEBP_QUALITY, method=6)
        im.save(path, "PNG", optimize=True, compress_level=9)

    png_bytes = path.stat().st_size
    webp_bytes = path.with_suffix(".webp").stat().st_size
    return orig_bytes, png_bytes, webp_bytes


def main() -> None:
    total_orig = 0
    total_png = 0
    total_webp = 0

    for path in sorted(ROOT.rglob("*.png")):
        if "node_modules" in path.parts or path.parent.name == "_originals":
            continue
        orig, png, webp = process(path)
        total_orig += orig
        total_png += png
        total_webp += webp
        saved = 100 - (png / orig * 100) if orig else 0
        print(
            f"{path.relative_to(ROOT)}: "
            f"{orig / 1024:.0f} KB -> PNG {png / 1024:.0f} KB (-{saved:.0f}%) "
            f"| WebP {webp / 1024:.0f} KB"
        )

    print("---")
    print(f"Total PNG: {total_orig / 1024 / 1024:.1f} MB -> {total_png / 1024 / 1024:.1f} MB")
    print(f"Total WebP: {total_webp / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
