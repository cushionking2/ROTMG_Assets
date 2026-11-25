"""Render a map (live or generated) with the real game sprites.
Ground tiles come from assets (category 'tile'). Objects (walls, props, enemies) are drawn on top, centred on the tile.
Native art is 8 px per tile; 16 px art covers 2x2 tiles.

Run: python -I tools/render_tiles.py <map.json> [--px 32] [--crop x,y,w,h] [--out name]
Without --crop it writes the whole map at 16 px per tile.
Output: maps/png/tiles_<name>.png
"""
import argparse, json, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cache = {}

def load_index():
    ix = json.load(open(os.path.join(ROOT, "assets", "index.json")))
    ground, objs = {}, {}
    for e in ix:
        m = e["files"].get("main")
        if not m:
            continue
        (ground if e["category"] == "tile" else objs).setdefault(e["id"], os.path.join(ROOT, m))
    return ground, objs

def sprite(path):
    if path not in _cache:
        _cache[path] = Image.open(path).convert("RGBA")
    return _cache[path]

def render(map_path, px=16, crop=None):
    d = json.load(open(map_path))
    w, h = d["width"], d["height"]
    gmap, omap = load_index()
    x0, y0, cw, ch = crop if crop else (0, 0, w, h)
    img = Image.new("RGBA", (cw * px, ch * px), (20, 20, 20, 255))
    missing = set()
    # pass 1: ground
    for y in range(y0, min(y0 + ch, h)):
        for x in range(x0, min(x0 + cw, w)):
            e = d["dict"][d["grid"][y * w + x]]
            g = e["ground"]
            if g == "Space":
                continue
            p = gmap.get(g)
            if not p:
                missing.add(g)
                continue
            img.alpha_composite(sprite(p).resize((px, px), Image.NEAREST), ((x - x0) * px, (y - y0) * px))
    # pass 2: objects, top rows first so lower objects overlap higher ones
    for y in range(y0, min(y0 + ch, h)):
        for x in range(x0, min(x0 + cw, w)):
            e = d["dict"][d["grid"][y * w + x]]
            for o in e.get("objs") or []:
                p = omap.get(o["id"])
                if not p:
                    missing.add(o["id"])
                    continue
                s = sprite(p)
                size = int(round(s.width / 8.0 * px))
                im = s.resize((size, size), Image.NEAREST)
                cx = (x - x0) * px + px // 2 - size // 2
                cy = (y - y0) * px + px // 2 - size // 2
                img.alpha_composite(im, (cx, cy))
    return img, missing

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("map")
    ap.add_argument("--px", type=int, default=16)
    ap.add_argument("--crop")
    ap.add_argument("--out")
    a = ap.parse_args()
    crop = tuple(int(v) for v in a.crop.split(",")) if a.crop else None
    img, missing = render(a.map, a.px, crop)
    name = a.out or os.path.basename(a.map).replace(".json", "")
    out = os.path.join(ROOT, "maps", "png", "tiles_" + name + ".png")
    img.convert("RGB").save(out)
    print(out, img.size, "no sprite for:", sorted(missing)[:10])
