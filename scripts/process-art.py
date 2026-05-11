#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".JPG", ".JPEG", ".PNG", ".WEBP", ".GIF"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compress, watermark, and classify photos into landscape/portrait web outputs."
    )
    parser.add_argument(
        "--source",
        default="art/original",
        help="Source directory containing original images.",
    )
    parser.add_argument(
        "--output-root",
        default="art",
        help="Root directory containing landscape/portrait output folders.",
    )
    parser.add_argument(
        "--horizontal-width",
        type=int,
        default=1600,
        help="Output width for horizontal images.",
    )
    parser.add_argument(
        "--horizontal-height",
        type=int,
        default=1067,
        help="Output height for horizontal images.",
    )
    parser.add_argument(
        "--vertical-width",
        type=int,
        default=1067,
        help="Output width for vertical images.",
    )
    parser.add_argument(
        "--vertical-height",
        type=int,
        default=1600,
        help="Output height for vertical images.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=82,
        help="JPEG quality for processed images.",
    )
    parser.add_argument(
        "--watermark",
        default="@Arrokoth",
        help="Watermark text.",
    )
    parser.add_argument(
        "--font",
        default="/System/Library/Fonts/Supplemental/SignPainter.ttc",
        help="Font file used for watermark text.",
    )
    parser.add_argument(
        "--suffix",
        default="-web",
        help="Suffix appended before the output extension.",
    )
    return parser.parse_args()


def iter_images(root: Path) -> list[Path]:
    return sorted(
        path for path in root.iterdir() if path.is_file() and path.suffix in IMAGE_EXTS
    )


def load_font(size: int, preferred_font: str | None = None) -> ImageFont.ImageFont:
    candidates = []
    if preferred_font:
        candidates.append(preferred_font)
    candidates.extend([
        "/System/Library/Fonts/Supplemental/SignPainter.ttc",
        "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc",
        "/System/Library/Fonts/Supplemental/Apple Chancery.ttf",
        "/System/Library/Fonts/Supplemental/Savoye LET.ttc",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/System/Library/Fonts/Avenir.ttc",
        "/System/Library/Fonts/Supplemental/Baskerville.ttc",
        "/System/Library/Fonts/Supplemental/Didot.ttc",
        "/System/Library/Fonts/Supplemental/GillSans.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ])
    for candidate in candidates:
        font_path = Path(candidate)
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def fit_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(
        image,
        size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )


def add_watermark(image: Image.Image, text: str, preferred_font: str | None = None) -> Image.Image:
    rgba = image.convert("RGBA")
    overlay = Image.new("RGBA", rgba.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = max(14, int(min(rgba.size) * 0.018))
    font = load_font(font_size, preferred_font=preferred_font)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    margin = max(8, int(min(rgba.size) * 0.012))
    x = rgba.width - text_w - margin
    y = rgba.height - text_h - margin

    draw.text(
        (x + 1, y + 1),
        text,
        font=font,
        fill=(0, 0, 0, 68),
    )
    draw.text(
        (x, y),
        text,
        font=font,
        fill=(255, 255, 255, 150),
    )

    return Image.alpha_composite(rgba, overlay).convert("RGB")


def output_path(source_path: Path, output_root: Path, suffix: str, orientation: str) -> Path:
    stem = source_path.stem.replace(" ", "-")
    return output_root / orientation / f"{stem}{suffix}.jpg"


def process_one(
    source_path: Path,
    output_root: Path,
    horizontal_size: tuple[int, int],
    vertical_size: tuple[int, int],
    quality: int,
    watermark: str,
    font: str | None,
    suffix: str,
) -> tuple[str, Path]:
    with Image.open(source_path) as original:
        image = ImageOps.exif_transpose(original)
        orientation = "horizontal" if image.width >= image.height else "vertical"
        image = image.convert("RGB")
        target_size = horizontal_size if orientation == "horizontal" else vertical_size
        image = fit_image(image, size=target_size)
        image = add_watermark(image, watermark, preferred_font=font)

    destination = output_path(source_path, output_root, suffix=suffix, orientation=orientation)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, format="JPEG", quality=quality, optimize=True, progressive=True)
    return orientation, destination


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    source_root = (repo_root / args.source).resolve()
    output_root = (repo_root / args.output_root).resolve()

    if not source_root.exists():
        raise SystemExit(f"Source directory not found: {source_root}")

    for folder in ("horizontal", "vertical"):
        (output_root / folder).mkdir(parents=True, exist_ok=True)

    images = iter_images(source_root)
    if not images:
        print(f"No images found in {source_root}")
        return

    processed = 0
    horizontal_size = (args.horizontal_width, args.horizontal_height)
    vertical_size = (args.vertical_width, args.vertical_height)
    for source_path in images:
        orientation, destination = process_one(
            source_path,
            output_root=output_root,
            horizontal_size=horizontal_size,
            vertical_size=vertical_size,
            quality=args.quality,
            watermark=args.watermark,
            font=args.font,
            suffix=args.suffix,
        )
        processed += 1
        print(f"{source_path.name} -> {orientation}/{destination.name}")

    print(f"Processed {processed} images from {source_root}")


if __name__ == "__main__":
    main()
