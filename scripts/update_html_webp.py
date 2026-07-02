"""Wrap PNG img tags with WebP picture sources in index.html."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"

IMG_RE = re.compile(
    r"<picture>\s*<source[^>]+>\s*<img([^>]*?)\ssrc=\"(\./[^\"]+\.png)\"([^>]*?)\s*/?\s*>\s*</picture>"
    r"|<img([^>]*?)\ssrc=\"(\./[^\"]+\.png)\"([^>]*?)\s*/?\s*>",
    re.IGNORECASE,
)


def wrap_img(match: re.Match[str]) -> str:
    if match.group(2):
        return match.group(0)
    before, src, after = match.group(4), match.group(5), match.group(6)
    webp = src[:-4] + ".webp"
    webp_path = ROOT / webp[2:].replace("/", "\\")
    if not webp_path.exists():
        return match.group(0)
    attrs = f'{before.strip()} src="{src}"{after}'.strip()
    return (
        f'<picture>'
        f'<source srcset="{webp}" type="image/webp">'
        f"<img {attrs}>"
        f"</picture>"
    )


def main() -> None:
    text = HTML.read_text(encoding="utf-8")
    updated = IMG_RE.sub(wrap_img, text)

    updated = updated.replace(
        'href="./backgroundblue.png"',
        'href="./backgroundblue.webp"',
    )
    updated = updated.replace(
        'href="./midnight_logo.png" fetchpriority="high">',
        'href="./midnight_logo.webp" fetchpriority="high">',
    )
    updated = updated.replace(
        'background-image: url("./backgroundblue.png");',
        'background-image: image-set(url("./backgroundblue.webp") type("image/webp"), url("./backgroundblue.png") type("image/png"));',
    )
    updated = updated.replace(
        'content="./midnight_logo.png"',
        'content="./midnight_logo.webp"',
    )
    updated = updated.replace(
        'if (ogImage) ogImage.content = origin + "/midnight_logo.png";',
        'if (ogImage) ogImage.content = origin + "/midnight_logo.webp";',
    )
    updated = updated.replace(
        'if (twitterImage) twitterImage.content = origin + "/midnight_logo.png";',
        'if (twitterImage) twitterImage.content = origin + "/midnight_logo.webp";',
    )

    HTML.write_text(updated, encoding="utf-8")
    count = updated.count('type="image/webp"')
    print(f"Updated index.html with {count} WebP picture sources.")


if __name__ == "__main__":
    main()
