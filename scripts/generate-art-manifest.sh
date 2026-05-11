#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ART_DIR="$ROOT_DIR/art"
MANIFEST="$ART_DIR/manifest.json"
MANIFEST_JS="$ART_DIR/manifest.js"
HORIZONTAL_DIR="$ART_DIR/horizontal"
VERTICAL_DIR="$ART_DIR/vertical"

python3 - "$ROOT_DIR" "$HORIZONTAL_DIR" "$VERTICAL_DIR" "$MANIFEST" "$MANIFEST_JS" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
horizontal_dir = Path(sys.argv[2])
vertical_dir = Path(sys.argv[3])
manifest_path = Path(sys.argv[4])
manifest_js_path = Path(sys.argv[5])
exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".JPG", ".JPEG", ".PNG", ".WEBP", ".GIF"}


def collect(folder: Path):
    if not folder.exists():
        return []
    return sorted(
        str(path.relative_to(root)).replace("\\", "/")
        for path in folder.iterdir()
        if path.is_file() and path.suffix in exts
    )


payload = {
    "horizontal": collect(horizontal_dir),
    "vertical": collect(vertical_dir),
}
flat = payload["horizontal"] + payload["vertical"]

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
    f.write("\n")

with open(manifest_js_path, "w", encoding="utf-8") as f:
    f.write("window.__ART_GROUPS__ = ")
    json.dump(payload, f, ensure_ascii=False, indent=2)
    f.write(";\n")
    f.write("window.__ART_IMAGES__ = ")
    json.dump(flat, f, ensure_ascii=False, indent=2)
    f.write(";\n")
PY

echo "Updated $MANIFEST and $MANIFEST_JS"
