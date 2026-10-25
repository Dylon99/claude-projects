#!/usr/bin/env python3
"""Build web-ready photos and photos.json from a folder of originals.

Layout of the source folder (subfolder name = gallery category):

    originals/
      landscape/  sunrise.jpg ...
      street/     tokyo-night.jpg ...

Outputs (relative to the site root):
    photos/full/<slug>.jpg    long edge <= --full px
    photos/thumbs/<slug>.jpg  long edge <= --thumb px
    photos.json               merged: titles/captions you edited are preserved

ALL metadata (EXIF incl. GPS, XMP, IPTC) is stripped from the published files.
Camera model and year are read from EXIF first and written to photos.json only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}
SITE_ROOT = Path(__file__).resolve().parent.parent
EXIF_MODEL, EXIF_DATETIME_ORIGINAL, EXIF_IFD = 0x0110, 0x9003, 0x8769
# Fields owned by the human editor; never overwritten on rebuild.
EDITABLE = ("title", "alt", "location", "featured", "category")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def read_exif(img: Image.Image) -> dict:
    exif = img.getexif()
    out = {}
    if model := exif.get(EXIF_MODEL):
        out["camera"] = str(model).strip()
    taken = exif.get_ifd(EXIF_IFD).get(EXIF_DATETIME_ORIGINAL)
    if taken and str(taken)[:4].isdigit():
        out["year"] = int(str(taken)[:4])
    return out


def save_resized(img: Image.Image, dest: Path, long_edge: int, quality: int) -> tuple[int, int]:
    im = img.copy()
    im.thumbnail((long_edge, long_edge), Image.Resampling.LANCZOS)
    # Drop carried-over metadata (EXIF/GPS, XMP, comments) before encoding.
    im.info = {}
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=quality, optimize=True, progressive=True)
    return im.size


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path, help="folder of original photos")
    ap.add_argument("--full", type=int, default=2400, help="long edge of full-size images (px)")
    ap.add_argument("--thumb", type=int, default=900, help="long edge of thumbnails (px)")
    ap.add_argument("--quality", type=int, default=82)
    ap.add_argument("--keep-samples", action="store_true", help="keep picsum sample entries")
    args = ap.parse_args()

    if not args.source.is_dir():
        ap.error(f"{args.source} is not a directory")

    manifest_path = SITE_ROOT / "photos.json"
    existing = {}
    if manifest_path.exists():
        for p in json.loads(manifest_path.read_text()).get("photos", []):
            if args.keep_samples or not p.get("src", "").startswith("https://picsum.photos"):
                existing[p.get("src")] = p

    photos, seen = [], set()
    for path in sorted(args.source.rglob("*")):
        if path.suffix.lower() not in EXTS or not path.is_file():
            continue
        rel = path.relative_to(args.source)
        category = rel.parts[0] if len(rel.parts) > 1 else "uncategorised"
        slug = slugify(f"{category}-{path.stem}")
        if slug in seen:
            print(f"skip duplicate slug: {rel}", file=sys.stderr)
            continue
        seen.add(slug)

        with Image.open(path) as raw:
            meta = read_exif(raw)
            img = ImageOps.exif_transpose(raw).convert("RGB")

        full_rel = f"photos/full/{slug}.jpg"
        w, h = save_resized(img, SITE_ROOT / full_rel, args.full, args.quality)
        thumb_rel = f"photos/thumbs/{slug}.jpg"
        save_resized(img, SITE_ROOT / thumb_rel, args.thumb, args.quality)

        entry = {"title": path.stem.replace("-", " ").replace("_", " ").title(),
                 "category": category, "src": full_rel, "thumb": thumb_rel,
                 "width": w, "height": h, **meta}
        prev = existing.pop(full_rel, {})
        entry.update({k: prev[k] for k in EDITABLE if k in prev})
        photos.append(entry)
        print(f"ok  {rel} -> {full_rel} ({w}x{h})")

    if args.keep_samples:
        photos.extend(existing.values())

    if photos and not any(p.get("featured") for p in photos):
        photos[0]["featured"] = True

    manifest_path.write_text(json.dumps({"photos": photos}, indent=2) + "\n")
    print(f"wrote {manifest_path.relative_to(SITE_ROOT)} with {len(photos)} photos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
