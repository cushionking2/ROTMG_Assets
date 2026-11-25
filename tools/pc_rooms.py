"""Extract rooms and corridors from captured Pirate Cave maps.
Method: structure mask (sand, wood, carpet, torch/wood walls) -> morphological opening removes thin planks ->
connected cores = rooms -> rest of the structure = corridors (planks).
Output: rooms/pirate_cave/<capture>.json and a summary printed to the console.
Run: python -I tools/pc_rooms.py [maps/live/*Pirate_Cave.json ...]
"""
import glob, json, os, sys
from collections import Counter, deque
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pc_classes import classes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "rooms", "pirate_cave")
os.makedirs(OUT, exist_ok=True)

ENEMY = set()
for x in json.load(open(os.path.join(ROOT, "work", "objects.json"))):
    if x["tag"] == "Object" and x.get("enemy"):
        ENEMY.add(x["id"])

def shift(m, dx, dy):
    r = np.zeros_like(m)
    h, w = m.shape
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    r[yd, xd] = m[ys, xs]
    return r

def erode(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out &= shift(m, dx, dy)
    return out

def dilate(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= shift(m, dx, dy)
    return out

def label(m):
    h, w = m.shape
    lab = np.zeros((h, w), int)
    n = 0
    for y in range(h):
        for x in range(w):
            if m[y, x] and not lab[y, x]:
                n += 1
                q = deque([(x, y)])
                lab[y, x] = n
                while q:
                    cx, cy = q.popleft()
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and m[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n
                            q.append((nx, ny))
    return lab, n

def extract(path, r=2):
    d = json.load(open(path))
    w, h, cls = classes(d)
    C = np.array(cls).reshape(h, w)
    struct = np.isin(C, list("SDCTBO"))
    # fill small enclosed holes (water pools inside cabins) so a cabin stays one room
    hl, hn = label(~struct)
    for k in range(1, hn + 1):
        ys, xs = np.nonzero(hl == k)
        touches_edge = ys.min() == 0 or xs.min() == 0 or ys.max() == h - 1 or xs.max() == w - 1
        if not touches_edge and len(xs) <= 80:
            struct[ys, xs] = True
    core = dilate(erode(struct, r), r) & struct          # opening
    lab, n = label(erode(struct, r))                      # room cores
    # grow each core back inside the opened mask (multi-source BFS)
    room = lab.copy()
    q = deque((x, y) for y, x in zip(*np.nonzero(lab)))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and core[ny, nx] and not room[ny, nx]:
                room[ny, nx] = room[y, x]
                q.append((nx, ny))
    corr = struct & (room == 0)
    clab, cn = label(corr)
    # objects per tile
    objs = {}
    for i, e in enumerate(d["dict"]):
        objs[i] = [o["id"] for o in e.get("objs", []) or []]
    grid = np.array(d["grid"]).reshape(h, w)
    rooms = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(room == k)
        if len(xs) < 20:
            continue
        x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
        bw, bh = x1 - x0 + 1, y1 - y0 + 1
        cc = Counter(C[y, x] for y, x in zip(ys, xs))
        mons, props = Counter(), Counter()
        for y, x in zip(ys, xs):
            for o in objs[grid[y, x]]:
                if o in ENEMY:
                    mons[o] += 1
                elif o.startswith("PC "):
                    props[o] += 1
        fill = len(xs) / float(bw * bh)
        rooms.append({"id": k, "x": x0, "y": y0, "w": bw, "h": bh, "area": int(len(xs)), "fill": round(fill, 2),
                      "ground": {a: int(b) for a, b in cc.most_common()}, "monsters": dict(mons), "props": dict(props.most_common(8))})
    # corridor adjacency
    for c in range(1, cn + 1):
        pass
    links = []
    for c in range(1, cn + 1):
        ys, xs = np.nonzero(clab == c)
        if len(xs) < 3:
            continue
        touch = set()
        for y, x in zip(ys, xs):
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and room[ny, nx]:
                    touch.add(int(room[ny, nx]))
        links.append({"tiles": int(len(xs)), "w": int(xs.max() - xs.min() + 1), "h": int(ys.max() - ys.min() + 1),
                      "rooms": sorted(touch)})
    return {"file": os.path.basename(path), "rooms": rooms, "corridors": links}

def kind(rm):
    g = rm["ground"]
    if g.get("C", 0) > 20:
        return "boss_ship"
    if g.get("T", 0) > 8:
        return "cabin"
    if rm["fill"] < 0.85 and g.get("D", 0) > 0.6 * rm["area"] and rm["area"] > 150:
        return "small_ship"
    if g.get("S", 0) > 0.6 * rm["area"]:
        return "island"
    if g.get("D", 0) > 0.6 * rm["area"]:
        return "deck" if rm["fill"] > 0.85 else "deck_irregular"
    return "other"

if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, "maps", "live", "*Pirate_Cave.json")))
    for f in files:
        res = extract(f)
        for rm in res["rooms"]:
            rm["kind"] = kind(rm)
        json.dump(res, open(os.path.join(OUT, res["file"]), "w"), indent=1)
        kc = Counter(rm["kind"] for rm in res["rooms"])
        print(res["file"][:15], "rooms", len(res["rooms"]), dict(kc), "corridors", len(res["corridors"]))
