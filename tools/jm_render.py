"""Render live captured maps (maps/live/*.json) to PNG previews (4 px per tile).
Run: python -I tools/jm_render.py            (all live maps)
     python -I tools/jm_render.py pirate      (only maps whose name matches)
Ground colour comes from a hash of the ground name. Objects whose id has
'wall' are dark. Other objects are a bright dot.
"""
import hashlib, json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPS = os.path.join(ROOT, "maps")
OUT = os.path.join(MAPS, "png")
os.makedirs(OUT, exist_ok=True)
S = 4

def col(name, lo=60, hi=220):
    h = hashlib.md5(name.encode()).digest()
    return tuple(lo + h[i] % (hi - lo) for i in range(3))

def render(entry):
    d = json.load(open(os.path.join(MAPS, entry["file"])))
    w, h = d["width"], d["height"]
    cells = []
    for e in d["dict"]:
        g = e.get("ground", "Space")
        base = (0, 0, 0) if g == "Space" else col(g)
        objs = [o.get("id", "") for o in (e.get("objs") or [])]
        kind = 0
        if objs:
            kind = 1 if any("wall" in o.lower() for o in objs) else 2
        cells.append((base, kind))
    img = Image.new("RGB", (w * S, h * S))
    px = img.load()
    for i, c in enumerate(d["grid"]):
        base, kind = cells[c] if c < len(cells) else ((255, 0, 255), 0)
        x, y = i % w, i // w
        if kind == 1:
            colr = (25, 25, 25)
        else:
            colr = base
        for dy in range(S):
            for dx in range(S):
                px[x * S + dx, y * S + dy] = colr
        if kind == 2:
            for dy in (1, 2):
                for dx in (1, 2):
                    px[x * S + dx, y * S + dy] = (255, 40, 40)
    fn = entry["file"].replace("jm/", "").replace("/", "_").replace(".json", ".png")
    img.save(os.path.join(OUT, fn))
    return fn

if __name__ == "__main__":
    cat = []
    for fn in sorted(os.listdir(os.path.join(MAPS, "live"))) if os.path.isdir(os.path.join(MAPS, "live")) else []:
        d = json.load(open(os.path.join(MAPS, "live", fn)))
        cat.append({"name": "LIVE_" + d["name"], "file": "live/" + fn, "w": d["width"], "h": d["height"]})
    pat = sys.argv[1].lower() if len(sys.argv) > 1 else None
    n = 0
    for e in cat:
        if pat and pat not in e["name"].lower():
            continue
        if e["w"] * e["h"] < 16 or e["w"] * e["h"] > 1000000:
            continue
        render(e)
        n += 1
    print("rendered", n)
