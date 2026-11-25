"""Convert collector captures (collector/captures/*.jsonl) into maps/ format.
Names come from work/objects.json (the extracted game XML).
Output: maps/live/<capture>.json   {name, seed, width, height, dict, grid, stats}
  dict entries use the same shape as the .jm maps: {"ground": name, "objs": [{"id": name}]}
  A tile with several objects keeps the first static one (walls first).
Run: python -I tools/capture_to_map.py [capture.jsonl ...]   (default: all)
"""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "maps", "live")
os.makedirs(OUT, exist_ok=True)

names = {"Ground": {}, "Object": {}}
for x in json.load(open(os.path.join(ROOT, "work", "objects.json"))):
    try:
        names[x["tag"]][int(x["type"], 16)] = x["id"]
    except (KeyError, ValueError):
        pass

# Maps that are not dungeons. Keep in sync with SKIP in collector/src/MapCollector.java.
SKIP = {"Nexus", "Realm of the Mad God"}

def convert(path):
    tiles = {}
    by_id = {}            # objectId -> (name, static, type, x, y), first sighting only
    info = None
    n_upd = 0
    n_sightings = 0
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r["kind"] == "mapinfo":
            info = r
        elif r["kind"] == "update":
            n_upd += 1
            for x, y, t in r["tiles"]:
                tiles[(x, y)] = t
            for oid, ot, x, y in r["objs"]:
                n_sightings += 1
                # one entry per object id: an object that leaves and re-enters view keeps its first position
                key = oid if oid != -1 else ("pos", int(x), int(y), ot)
                if key in by_id:
                    continue
                nm = names["Object"].get(ot, "unknown_0x%x" % ot)
                low = nm.lower()
                static = ("wall" in low) or ("pillar" in low) or ("tree" in low) or ("rock" in low)
                by_id[key] = (nm, static, ot, int(x), int(y))
    objs = {}             # tile -> list of (name, static); static objects first
    for nm, static, ot, x, y in by_id.values():
        objs.setdefault((x, y), []).append((nm, static))
    for lst in objs.values():
        lst.sort(key=lambda v: not v[1])
    if not info or not tiles or info["name"] in SKIP:
        return None
    w, h = info["width"], info["height"]
    dct, lookup, grid = [], {}, [0] * (w * h)
    def idx(entry):
        k = json.dumps(entry, sort_keys=True)
        if k not in lookup:
            lookup[k] = len(dct)
            dct.append(entry)
        return lookup[k]
    empty = idx({"ground": "Space"})
    grid = [empty] * (w * h)
    for (x, y), t in tiles.items():
        if 0 <= x < w and 0 <= y < h:
            e = {"ground": names["Ground"].get(t, "unknown_0x%x" % t)}
            if (x, y) in objs:
                e["objs"] = [{"id": n} for n, _ in objs[(x, y)]]
            grid[y * w + x] = idx(e)
    missing_t = sum(1 for t in set(tiles.values()) if t not in names["Ground"])
    return {"name": info["name"], "displayName": info["displayName"], "seed": info["seed"],
            "version": info["version"], "width": w, "height": h, "dict": dct, "grid": grid,
            "stats": {"updates": n_upd, "tiles": len(tiles), "objects": len(by_id), "sightings": n_sightings,
                      "coverage": round(len(tiles) / float(w * h), 3), "unknown_tile_ids": missing_t}}

if __name__ == "__main__":
    files = sys.argv[1:] or sorted(f for f in glob.glob(os.path.join(ROOT, "collector", "captures", "*.jsonl")) if not f.endswith(".events.jsonl"))
    for f in files:
        m = convert(f)
        if not m:
            print("skip (no tiles):", os.path.basename(f))
            continue
        out = os.path.join(OUT, os.path.basename(f).replace(".jsonl", ".json"))
        json.dump(m, open(out, "w"), separators=(",", ":"))
        print(os.path.basename(out), m["width"], "x", m["height"], m["stats"])
