"""Render extracted rooms with ids on top of the class map. Run: python -I tools/pc_debug_render.py <maps/live/x.json>"""
import json, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pc_classes import classes, COL
import pc_rooms

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = sys.argv[1]
s = 7
d = json.load(open(path))
w, h, cls = classes(d)
res = pc_rooms.extract(path)
img = Image.new("RGB", (w * s, h * s))
dr = ImageDraw.Draw(img)
for i, c in enumerate(cls):
    x, y = i % w, i // w
    dr.rectangle([x * s, y * s, x * s + s - 1, y * s + s - 1], fill=COL[c])
for rm in res["rooms"]:
    dr.rectangle([rm["x"] * s, rm["y"] * s, (rm["x"] + rm["w"]) * s, (rm["y"] + rm["h"]) * s], outline=(255, 255, 255))
    dr.text((rm["x"] * s + 3, rm["y"] * s + 3), str(rm["id"]), fill=(255, 255, 0))
out = os.path.join(ROOT, "maps", "png", "pc_rooms_" + os.path.basename(path).replace(".json", ".png"))
img.save(out)
print(out)
for c in res["corridors"]:
    if len(c["rooms"]) != 2:
        print("corridor touching", c["rooms"], "tiles", c["tiles"], c["w"], "x", c["h"])
