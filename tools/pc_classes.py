"""Classify Pirate Cave tiles into simple classes and render a class map.
Classes: V void (not sent), W water, S sand, D wood floor, C carpet, X cave wall, B wood wall, T torch wall, O other.
Run: python -I tools/pc_classes.py <maps/live/xxx.json> [scale]  -> maps/png/pc_class_<name>.png
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COL = {"V": (30, 30, 30), "W": (40, 90, 200), "S": (230, 210, 140), "D": (150, 90, 40), "C": (220, 40, 40),
       "X": (0, 0, 0), "B": (90, 50, 20), "T": (255, 160, 0), "O": (120, 200, 120)}

def tile_class(entry):
    g = entry["ground"]
    objs = [o["id"] for o in entry.get("objs", []) or []]
    if g == "Space":
        return "V"
    if "PC Cave Wall" in objs:
        return "X"
    if "PC Torch Wall" in objs:
        return "T"
    if "PC Wood Wall" in objs or "PC Book Wall" in objs:
        return "B"
    if "Water" in g:
        return "W"
    if "Sand" in g:
        return "S"
    if "Carpet" in g:
        return "C"
    if "Wood" in g:
        return "D"
    return "O"

def classes(d):
    cls = [tile_class(e) for e in d["dict"]]
    w, h = d["width"], d["height"]
    return w, h, [cls[i] for i in d["grid"]]

if __name__ == "__main__":
    path = sys.argv[1]
    s = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    d = json.load(open(path))
    w, h, grid = classes(d)
    img = Image.new("RGB", (w * s, h * s))
    px = img.load()
    for i, c in enumerate(grid):
        x, y = i % w, i // w
        for dy in range(s):
            for dx in range(s):
                px[x * s + dx, y * s + dy] = COL[c]
    out = os.path.join(ROOT, "maps", "png", "pc_class_" + os.path.basename(path).replace(".json", ".png"))
    img.save(out)
    print(out)
