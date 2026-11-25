"""Summarize enemy behaviour from collector event files.
Input : collector/captures/*.events.jsonl   (one per map visit)
Output: behaviors/<capture>.md and behaviors/<capture>.json
Per enemy type: count, max HP, speed, shot patterns, shot interval, HP range of each
shot type, text lines. Also loot bags, portals, notices and teleports.
Names come from work/objects.json. Run: python -I tools/analyze_events.py [file ...]
Stat numbers: 0 max HP, 1 HP, 29 condition, 31 name, 8-19 inventory slots.
"""
import glob, json, math, os, statistics, sys
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "behaviors")
os.makedirs(OUT, exist_ok=True)

OBJ = {}
for x in json.load(open(os.path.join(ROOT, "work", "objects.json"))):
    if x["tag"] == "Object":
        try:
            OBJ[int(x["type"], 16)] = x
        except ValueError:
            pass

# Maps that are not dungeons. Keep in sync with SKIP in collector/src/MapCollector.java.
SKIP_FILES = ("_Nexus.", "_Realm_of_the_Mad_God.")

def nm(t):
    o = OBJ.get(t)
    return (o.get("display") or o["id"]) if o else "unknown_0x%x" % t

def is_enemy(t):
    o = OBJ.get(t)
    return bool(o and o.get("enemy"))

def med(v):
    return round(statistics.median(v), 2) if v else None

def analyze(path):
    otype, pos, stat, first = {}, {}, defaultdict(dict), {}
    last_pos_t = {}
    speeds = defaultdict(list)       # type -> tile/s samples (moving samples only)
    still = Counter(); moved = Counter()
    shots = defaultdict(lambda: defaultdict(list))   # type -> btype -> [(n, inc, dmg, hpfrac)]
    last_shot = {}                   # (owner, btype) -> t
    intervals = defaultdict(lambda: defaultdict(list))
    texts = defaultdict(set)
    notes, gotos, loot, portals = Counter(), Counter(), [], []
    types_seen = Counter()
    self_id = None
    quest = []
    n_ticks = 0
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        k = r["k"]
        if k == "self":
            self_id = r["obj"]
        elif k == "upd":
            for oid, t, x, y, st in r["new"]:
                if oid not in otype:
                    types_seen[t] += 1
                otype[oid] = t
                if x is not None:
                    pos[oid] = (x, y)
                for sn, sv in st:
                    stat[oid][sn] = sv
                nmv = OBJ.get(t, {}).get("id", "")
                if "bag" in nmv.lower() or "Bag" in nmv:
                    items = [sv for sn, sv in st if 8 <= sn <= 19 and sv != -1]
                    loot.append((nm(t), items))
                if "ortal" in nmv:
                    portals.append((nm(t), [sv for sn, sv in st if sn == 31]))
            for oid in r["drop"]:
                pos.pop(oid, None)
        elif k == "tick":
            n_ticks += 1
            t_srv = r["srv"] / 1000.0
            for oid, x, y, st in r["s"]:
                for sn, sv in st:
                    stat[oid][sn] = sv
                if x is None:
                    continue
                t = otype.get(oid)
                if oid in pos and t is not None and oid in last_pos_t:
                    dt = t_srv - last_pos_t[oid]
                    if 0.05 < dt < 2.0:
                        d = math.hypot(x - pos[oid][0], y - pos[oid][1])
                        if d > 0.01:
                            moved[t] += 1
                            speeds[t].append(d / dt)
                        else:
                            still[t] += 1
                pos[oid] = (x, y)
                last_pos_t[oid] = t_srv
        elif k == "eshoot":
            oid = r["owner"]
            t = otype.get(oid)
            if t is None:
                continue
            mx, hp = stat[oid].get(0), stat[oid].get(1)
            frac = round(hp / mx, 2) if mx and hp is not None else None
            shots[t][r["btype"]].append((r["n"], round(r["inc"], 3), r["dmg"], frac))
            key = (oid, r["btype"])
            if key in last_shot:
                dtm = (r["t"] - last_shot[key]) / 1000.0
                if dtm < 20:
                    intervals[t][r["btype"]].append(dtm)
            last_shot[key] = r["t"]
        elif k == "text":
            t = otype.get(r["obj"])
            texts[nm(t) if t is not None else r["name"] or "?"].add(r["text"])
        elif k == "notif":
            notes[r["msg"]] += 1
        elif k == "goto":
            t = otype.get(r["obj"])
            if t is not None and r["obj"] != self_id:
                gotos[nm(t)] += 1
        elif k == "quest":
            quest.append(r["obj"])

    res = {"file": os.path.basename(path), "ticks": n_ticks, "enemies": {}}
    max_hp = defaultdict(list)
    for oid, t in otype.items():
        if is_enemy(t) and 0 in stat[oid]:
            max_hp[t].append(stat[oid][0])
    for t, cnt in types_seen.most_common():
        if not is_enemy(t):
            continue
        e = {"count": cnt, "max_hp": med(max_hp[t]),
             "speed_tiles_per_s": med(speeds[t]),
             "moving_fraction": round(moved[t] / float(moved[t] + still[t]), 2) if moved[t] + still[t] else None,
             "shots": {}}
        for bt, lst in shots[t].items():
            ns = Counter(x[0] for x in lst)
            incs = Counter(x[1] for x in lst)
            dm = [x[2] for x in lst]
            fr = [x[3] for x in lst if x[3] is not None]
            e["shots"][str(bt)] = {"count": len(lst), "num_shots": dict(ns.most_common(3)),
                                  "angle_inc": dict(incs.most_common(3)), "damage": med(dm),
                                  "interval_s": med(intervals[t][bt]),
                                  "interval_min_s": round(min(intervals[t][bt]), 2) if intervals[t][bt] else None,
                                  "hp_fraction_range": [min(fr), max(fr)] if fr else None}
        res["enemies"][nm(t)] = e
    res["text"] = {k: sorted(v)[:10] for k, v in texts.items()}
    res["notifications"] = dict(notes.most_common(20))
    res["teleports"] = dict(gotos.most_common(20))
    res["loot_bags"] = Counter(("%s: %s" % (n, sorted(i))) for n, i in loot).most_common(30)
    res["portals"] = portals[:20]
    res["quest_targets"] = [nm(otype[o]) for o in quest if o in otype][:10]
    return res

def write_md(res, path):
    L = ["# Behaviour summary: " + res["file"], "", "Ticks: %d" % res["ticks"], ""]
    L += ["## Enemies", ""]
    for name, e in sorted(res["enemies"].items(), key=lambda kv: -kv[1]["count"]):
        L.append("### %s (x%d)" % (name, e["count"]))
        L.append("- Max HP: %s. Speed: %s tiles/s. Moving fraction: %s." % (e["max_hp"], e["speed_tiles_per_s"], e["moving_fraction"]))
        for bt, s in e["shots"].items():
            L.append("- Bullet type %s: %d shots, per volley %s, angle step %s, damage %s, interval median %s s (min %s), at HP fraction %s"
                     % (bt, s["count"], s["num_shots"], s["angle_inc"], s["damage"], s["interval_s"], s["interval_min_s"], s["hp_fraction_range"]))
        L.append("")
    for title, key in (("Text lines", "text"), ("Notifications", "notifications"), ("Teleports", "teleports"),
                       ("Portals", "portals"), ("Quest targets", "quest_targets"), ("Loot bags", "loot_bags")):
        L += ["## " + title, "", "```", json.dumps(res[key], indent=1, ensure_ascii=False), "```", ""]
    open(path, "w", encoding="utf-8").write("\n".join(L))

if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, "collector", "captures", "*.events.jsonl")))
    for f in files:
        if any(x in os.path.basename(f) for x in SKIP_FILES):
            print("skip (not a dungeon):", os.path.basename(f))
            continue
        res = analyze(f)
        stem = os.path.basename(f).replace(".events.jsonl", "")
        json.dump(res, open(os.path.join(OUT, stem + ".json"), "w"), indent=1)
        write_md(res, os.path.join(OUT, stem + ".md"))
        print(stem, "enemy types:", len(res["enemies"]), "ticks:", res["ticks"])
