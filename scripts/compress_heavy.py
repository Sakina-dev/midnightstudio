"""Second pass: aggressively optimize remaining heavy PNGs."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

TARGETS = {
    "santeencommun/chartegraphique.png": 1400,
    "santeencommun/flyer.png": 1800,
    "backgroundblue.png": 1440,
}


def prepare(im: Image.Image) -> Image.Image:
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        return im.convert("RGBA")
    return im.convert("RGB")


def main() -> None:
    for rel, max_w in TARGETS.items():
        path = ROOT / rel.replace("/", "\\")
        if not path.exists():
            continue
        orig = path.stat().st_size
        with Image.open(path) as source:
            im = prepare(source)
            w, h = im.size
            if w > max_w:
                ratio = max_w / w
                im = im.resize((max_w, int(h * ratio)), Image.Resampling.LANCZOS)
            im.save(path.with_suffix(".webp"), "WEBP", quality=78, method=6)
            im.save(path, "PNG", optimize=True, compress_level=9)
        png = path.stat().st_size
        webp = path.with_suffix(".webp").stat().st_size
        print(f"{rel}: {orig/1024:.0f} KB -> PNG {png/1024:.0f} KB | WebP {webp/1024:.0f} KB")


if __name__ == "__main__":
    main()
