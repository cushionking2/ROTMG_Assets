"""Pirate Cave generator, built from live captures only (build 7.2.0.1.0).

  python -I tools/pc_gen.py params          measure parameters -> rooms/pirate_cave_params.json
  python -I tools/pc_gen.py gen 1 2 3       generate maps with seeds -> maps/generated/pc_<seed>.json + .png
  python -I tools/pc_gen.py compare 40      generate 40 maps and compare statistics with the real maps

Model (all numbers measured from the captures, see docs/pirate_cave_findings.md):
  main path  : spawn island (circle 20) -> 4 rooms -> boss ship (41x21), always 5 hops
  branches   : extra rooms attach to random rooms (total 16 to 19), tree only, no loops
  gap        : 4 to 7 tiles between linked rooms, planks 2 tiles wide
  bay        : water up to 4 tiles from any structure, one ring of cave wall at 5
Limits: props and monsters are sampled, not placed by a measured rule. Decks use a guessed floor pattern for vertical wood.
"""
import glob, json, math, os, random, sys
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
from pc_classes import classes
import pc_rooms, pc_graph

PARAMS = os.path.join(ROOT, "rooms", "pirate_cave_params.json")
GEN = os.path.join(ROOT, "maps", "generated")
SIZE = 128
CHAIN_P = float(os.environ.get("PC_CHAIN_P", "0.33"))   # chance a new room extends the newest branch
FIXED_KINDS = ("boss_ship", "cabin", "small_ship")

# ---------------------------------------------------------------- parameters

def load_map(path):
    d = json.load(open(path))
    w, h = d["width"], d["height"]
    G = np.array([d["dict"][i]["ground"] for i in d["grid"]], dtype=object).reshape(h, w)
    O = np.array([(d["dict"][i].get("objs") or [{}])[0].get("id") for i in d["grid"]], dtype=object).reshape(h, w)
    return d, G, O

def build_params():
    enemy = pc_rooms.ENEMY
    P = {"n_total": [], "path_mid": [], "off_kinds": [], "decks": [], "island_d": [], "gaps": [],
         "templates": {}, "pop": defaultdict(lambda: {"mon_n": [], "mon": Counter(), "prop_n": [], "prop": Counter()}),
         "water": defaultdict(Counter), "cracked": Counter(), "sand": Counter(), "wprops_n": [], "wprops": Counter()}
    samples = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(ROOT, "maps", "live", "*Pirate_Cave.json"))):
        d, G, O = load_map(f)
        w, h, cls = classes(d)
        C = np.array(cls).reshape(h, w)
        r = json.load(open(os.path.join(ROOT, "rooms", "pirate_cave", os.path.basename(f))))
        rooms = {x["id"]: x for x in r["rooms"]}
        a = pc_graph.analyze(os.path.join(ROOT, "rooms", "pirate_cave", os.path.basename(f)))
        P["n_total"].append(a["rooms"])
        rooms2, adj, edges = pc_graph.graph(r)
        spawn = [i for i, x in rooms.items() if x["kind"] == "island" and x["w"] >= 20][0]
        boss = [i for i, x in rooms.items() if x["kind"] == "boss_ship"][0]
        d1, par = pc_graph.bfs(adj, spawn)
        path, u = [], boss
        while u is not None:
            path.append(u); u = par[u]
        path.reverse()
        for i in path[1:-1]:
            P["path_mid"].append(rooms[i]["kind"])
        for i, x in rooms.items():
            if i not in path:
                P["off_kinds"].append(x["kind"])
        for (p, q) in edges:
            A, B = rooms[p], rooms[q]
            gx = max(A["x"] - (B["x"] + B["w"]), B["x"] - (A["x"] + A["w"]))
            gy = max(A["y"] - (B["y"] + B["h"]), B["y"] - (A["y"] + A["h"]))
            if (gx >= 0) != (gy >= 0):
                P["gaps"].append(max(gx, gy))
        for i, x in rooms.items():
            k = x["kind"]
            y0, y1, x0, x1 = x["y"], x["y"] + x["h"], x["x"], x["x"] + x["w"]
            sub_g, sub_o = G[y0:y1, x0:x1], O[y0:y1, x0:x1]
            mons = [o for o in sub_o.flatten() if o in enemy]
            props = [o for o in sub_o.flatten() if o and o not in enemy and "Wall" not in o and "Loot" not in o]
            pk = k if k != "island" or x["w"] < 20 else "spawn"
            pp = P["pop"][pk]
            pp["mon_n"].append(len(mons)); pp["mon"].update(mons)
            pp["prop_n"].append(len(props)); pp["prop"].update(props)
            if k == "deck":
                names = Counter(g for g in sub_g.flatten() if g != "Space")
                horiz = sum(v for g, v in names.items() if "Horizontal" in g) >= sum(v for g, v in names.items() if "Vertical" in g)
                P["decks"].append([x["w"], x["h"], int(horiz)])
                for g, v in names.items():
                    if "Cracked" in g:
                        P["cracked"][g.split("Wood ")[1]] += v
                P["cracked"]["_total"] += sum(v for g, v in names.items() if "Edge" not in g)
            if k == "island" and x["w"] < 20:
                P["island_d"].append(max(x["w"], x["h"]))
            if k == "island":
                for g in sub_g.flatten():
                    if "Sand" in g:
                        P["sand"][g] += 1
            if k in FIXED_KINDS or pk == "spawn":
                samples[(pk, x["w"], x["h"])].append((sub_g, sub_o))
        wo = [O[y, x] for y, x in zip(*np.nonzero(C == "W")) if O[y, x] and "Wall" not in O[y, x]]
        P["wprops_n"].append(len(wo)); P["wprops"].update(wo)
        # water shade by distance
        S = np.isin(C, list("SDCTBO"))
        prev = S
        for dist in range(1, 6):
            D = pc_rooms.dilate(S, dist)
            ring = D & ~prev
            prev = D
            for g in G[ring & (C == "W")]:
                P["water"][str(dist)][g] += 1
    # fixed templates: per-cell majority, object kept when present in >= 60 percent
    for key, lst in samples.items():
        n = len(lst)
        gg, oo = lst[0][0].shape, lst[0][1].shape
        tg = [[None] * gg[1] for _ in range(gg[0])]
        to = [[None] * gg[1] for _ in range(gg[0])]
        for y in range(gg[0]):
            for x in range(gg[1]):
                tg[y][x] = Counter(s[0][y, x] for s in lst).most_common(1)[0][0]
                oc = Counter(s[1][y, x] for s in lst if s[1][y, x])
                if oc:
                    o, c = oc.most_common(1)[0]
                    if c >= 0.6 * n:
                        to[y][x] = o
        P["templates"]["%s|%d|%d" % key] = {"kind": key[0], "w": key[1], "h": key[2], "n": n, "ground": tg, "obj": to}
    P["pop"] = {k: {"mon_n": v["mon_n"], "mon": dict(v["mon"]), "prop_n": v["prop_n"], "prop": dict(v["prop"])} for k, v in P["pop"].items()}
    P["water"] = {k: dict(v) for k, v in P["water"].items()}
    for k in ("cracked", "sand", "wprops"):
        P[k] = dict(P[k])
    json.dump(P, open(PARAMS, "w"))
    print("params:", {k: (len(v) if hasattr(v, "__len__") else v) for k, v in P.items()})
    print("templates:", list(P["templates"]))

# ---------------------------------------------------------------- generation

class Room:
    def __init__(self, kind, w, h, tmpl=None, orient=1):
        self.kind, self.w, self.h, self.tmpl, self.orient = kind, w, h, tmpl, orient
        self.x = self.y = 0
        self.children = []
        self.parent = None
        self.depth = 0
        self.bd = 0          # distance from the main path (0 on the path)

    def rect(self, m=0):
        return (self.x - m, self.y - m, self.x + self.w + m, self.y + self.h + m)

def hit(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

class Gen:
    def __init__(self, P, seed):
        self.P, self.rng = P, random.Random(seed)
        self.rooms, self.planks = [], []   # planks: (x0,y0,x1,y1,vertical,parent,child)

    def make(self, kind):
        P, rng = self.P, self.rng
        T = P["templates"]
        if kind == "spawn":
            return Room("spawn", 20, 20, T["spawn|20|20"])
        if kind == "boss_ship":
            return Room(kind, 41, 21, T["boss_ship|41|21"])
        if kind == "cabin":
            t = [v for k, v in T.items() if v["kind"] == "cabin"][0]
            return Room(kind, t["w"], t["h"], t)
        if kind == "small_ship":
            t = rng.choice([v for k, v in T.items() if v["kind"] == "small_ship"])
            return Room(kind, t["w"], t["h"], t)
        if kind == "island":
            dd = rng.choice(P["island_d"])
            return Room(kind, dd, dd)
        w, h, o = rng.choice(P["decks"])
        return Room("deck", w, h, None, o)

    def collide(self, rm, ignore=()):
        r = rm.rect(1)
        for o in self.rooms:
            if o is not rm and o not in ignore and hit(r, o.rect(0)):
                return True
            if o is not rm and o in ignore and hit(rm.rect(0), o.rect(0)):
                return True
        for p in self.planks:
            if hit(r, (p[0], p[1], p[2], p[3])) and rm is not p[5] and rm is not p[6]:
                return True
        return False

    def attach(self, parent, child):
        rng = self.rng
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        rng.shuffle(dirs)
        for dx, dy in dirs:
            gap = rng.choice(self.P["gaps"])
            if dx:
                child.x = parent.x + parent.w + gap if dx > 0 else parent.x - gap - child.w
                lo = parent.y - child.h + 6
                hi = parent.y + parent.h - 6
                if hi < lo:
                    continue
                child.y = rng.randint(lo, hi)
                a0 = max(parent.y, child.y) + 3
                a1 = min(parent.y + parent.h, child.y + child.h) - 3
                if a1 - a0 < 2:
                    continue
                if parent.kind in ("spawn", "island") or child.kind in ("island",):
                    mid = (a0 + a1) // 2
                    a0 = max(a0, mid - 3); a1 = min(a1, mid + 3)
                py = rng.randint(a0, max(a0, a1 - 2))
                if dx > 0:
                    pl = (parent.x + parent.w, py, child.x, py + 2, False, parent, child)
                else:
                    pl = (child.x + child.w, py, parent.x, py + 2, False, parent, child)
            else:
                child.y = parent.y + parent.h + gap if dy > 0 else parent.y - gap - child.h
                lo = parent.x - child.w + 6
                hi = parent.x + parent.w - 6
                if hi < lo:
                    continue
                child.x = rng.randint(lo, hi)
                a0 = max(parent.x, child.x) + 3
                a1 = min(parent.x + parent.w, child.x + child.w) - 3
                if a1 - a0 < 2:
                    continue
                if parent.kind in ("spawn", "island") or child.kind in ("island",):
                    mid = (a0 + a1) // 2
                    a0 = max(a0, mid - 3); a1 = min(a1, mid + 3)
                px = rng.randint(a0, max(a0, a1 - 2))
                if dy > 0:
                    pl = (px, parent.y + parent.h, px + 2, child.y, True, parent, child)
                else:
                    pl = (px, child.y + child.h, px + 2, parent.y, True, parent, child)
            if self.collide(child, ignore=(parent,)):
                continue
            # plank region must not cross other rooms
            pr = (pl[0], pl[1], pl[2], pl[3])
            if any(hit(pr, o.rect(0)) for o in self.rooms if o is not parent and o is not child):
                continue
            if any(hit(pr, (q[0], q[1], q[2], q[3])) for q in self.planks):
                continue
            self.rooms.append(child)
            self.planks.append(pl)
            child.parent = parent
            child.depth = parent.depth + 1
            parent.children.append(child)
            return True
        return False

    def build_path(self, parent, step):
        P, rng = self.P, self.rng
        for _ in range(12):
            kind = "boss_ship" if step == 5 else rng.choice(P["path_mid"])
            child = self.make(kind)
            if self.attach(parent, child):
                if step == 5 or self.build_path(child, step + 1):
                    return True
                self.remove_subtree(child)
        return False

    def remove_subtree(self, rm):
        for c in list(rm.children):
            self.remove_subtree(c)
        self.planks = [p for p in self.planks if p[6] is not rm]
        if rm in self.rooms:
            self.rooms.remove(rm)
        if rm.parent:
            rm.parent.children.remove(rm)

    def run(self):
        P, rng = self.P, self.rng
        root = self.make("spawn")
        self.rooms = [root]
        if not self.build_path(root, 1):
            return None
        total = rng.choice(P["n_total"])
        tries = 0
        last = None
        while len(self.rooms) < total and tries < 400:
            tries += 1
            if last is not None and last.parent is not None and rng.random() < CHAIN_P and last in self.rooms:
                parent = last            # continue the newest branch (real maps are chain-like)
            else:
                parent = rng.choice(self.rooms)
            if parent.kind == "boss_ship" and rng.random() < 0.7:
                continue
            if parent.depth >= 11:
                continue
            kind = rng.choice([k for k in P["off_kinds"]])
            nr = self.make(kind)
            nr.bd = parent.bd + 1
            if nr.bd > 6:                    # real maps: branches are at most 6 rooms deep
                continue
            if self.attach(parent, nr):
                last = nr
        if len(self.rooms) < min(P["n_total"]):
            return None
        xs0 = min(r.x for r in self.rooms); xs1 = max(r.x + r.w for r in self.rooms)
        ys0 = min(r.y for r in self.rooms); ys1 = max(r.y + r.h for r in self.rooms)
        if xs1 - xs0 > SIZE - 12 or ys1 - ys0 > SIZE - 12:
            return None
        ox, oy = (SIZE - (xs1 - xs0)) // 2 - xs0, (SIZE - (ys1 - ys0)) // 2 - ys0
        for r in self.rooms:
            r.x += ox; r.y += oy
        self.planks = [(p[0] + ox, p[1] + oy, p[2] + ox, p[3] + oy, p[4], p[5], p[6]) for p in self.planks]
        return self.rooms

    # ------------------------------------------------------------ rasterize
    def raster(self):
        P, rng = self.P, self.rng
        G = np.full((SIZE, SIZE), "Space", dtype=object)
        O = np.full((SIZE, SIZE), None, dtype=object)
        S = np.zeros((SIZE, SIZE), bool)
        sand_w = P["sand"]
        for rm in self.rooms:
            if rm.tmpl:
                t = rm.tmpl
                for y in range(rm.h):
                    for x in range(rm.w):
                        g = t["ground"][y][x]
                        if g not in ("Space", "Composite") and "Water" not in g and not (t["obj"][y][x] == "PC Cave Wall"):
                            G[rm.y + y, rm.x + x] = g
                            O[rm.y + y, rm.x + x] = t["obj"][y][x]
                            S[rm.y + y, rm.x + x] = True
            elif rm.kind == "island":
                cx, cy, r = rm.x + rm.w / 2.0 - 0.5, rm.y + rm.h / 2.0 - 0.5, rm.w / 2.0
                for y in range(rm.h):
                    for x in range(rm.w):
                        if math.hypot(rm.x + x - cx, rm.y + y - cy) <= r - 0.3:
                            G[rm.y + y, rm.x + x] = "PC Sand Alt" if rng.random() < 0.07 else "PC Sand"
                            S[rm.y + y, rm.x + x] = True
            else:
                orient = "Horizontal" if rm.orient else "Vertical"
                ck = P["cracked"]; tot = ck.get("_total", 1)
                crack = [(k, v) for k, v in ck.items() if k != "_total" and k.startswith(("1", "2", "3", "4"))]
                for y in range(rm.h):
                    for x in range(rm.w):
                        edge = (y if rm.orient else x)
                        last = (rm.h - 1 if rm.orient else rm.w - 1)
                        if edge == 0:
                            g = "PC %s Wood Edge L" % orient
                        elif edge == last:
                            g = "PC %s Wood Edge R" % orient
                        elif crack and rng.random() < sum(v for k, v in crack) / float(tot) / 2.0:
                            g = "PC %s Wood Cracked %s" % (orient, rng.choice(["1", "2", "3", "4"]))
                        else:
                            g = "PC %s Wood" % orient
                        G[rm.y + y, rm.x + x] = g
                        S[rm.y + y, rm.x + x] = True
        for (x0, y0, x1, y1, vert, a, b) in self.planks:
            # fill the gap, then extend into both rooms until a room tile is met
            cells = []
            if vert:
                for x in (x0, x0 + 1):
                    cells += [(x, y) for y in range(y0, y1)]
                    for y in range(y0 - 1, y0 - 13, -1):
                        if S[y, x]: break
                        cells.append((x, y))
                    for y in range(y1, y1 + 12):
                        if S[y, x]: break
                        cells.append((x, y))
                name = "PC Vertical Wood"
            else:
                for y in (y0, y0 + 1):
                    cells += [(x, y) for x in range(x0, x1)]
                    for x in range(x0 - 1, x0 - 13, -1):
                        if S[y, x]: break
                        cells.append((x, y))
                    for x in range(x1, x1 + 12):
                        if S[y, x]: break
                        cells.append((x, y))
                name = "PC Horizontal Wood"
            for (x, y) in cells:
                if 0 <= x < SIZE and 0 <= y < SIZE and not S[y, x]:
                    G[y, x] = name
            for (x, y) in cells:
                if 0 <= x < SIZE and 0 <= y < SIZE:
                    S[y, x] = True
        # bay
        prev = S
        wt = {k: (list(v.keys()), list(v.values())) for k, v in P["water"].items()}
        for dist in range(1, 6):
            D = pc_rooms.dilate(S, dist)
            ring = D & ~prev
            prev = D
            ys, xs = np.nonzero(ring)
            for y, x in zip(ys, xs):
                if dist <= 4:
                    names, wts = wt[str(dist)]
                    G[y, x] = rng.choices(names, wts)[0]
                else:
                    G[y, x] = "Composite"; O[y, x] = "PC Cave Wall"
        # fill small enclosed void holes with cave wall
        hl, hn = pc_rooms.label(G == "Space")
        for k in range(1, hn + 1):
            ys, xs = np.nonzero(hl == k)
            if len(xs) <= 40 and ys.min() > 0 and xs.min() > 0 and ys.max() < SIZE - 1 and xs.max() < SIZE - 1:
                for y, x in zip(ys, xs):
                    G[y, x] = "Composite"; O[y, x] = "PC Cave Wall"
        self.S = S
        return G, O

    def populate(self, G, O):
        P, rng = self.P, self.rng
        enemy = pc_rooms.ENEMY
        for rm in self.rooms:
            pk = rm.kind
            pop = P["pop"].get(pk)
            if not pop:
                continue
            cells = [(rm.x + x, rm.y + y) for y in range(rm.h) for x in range(rm.w)
                     if G[rm.y + y, rm.x + x] not in ("Space",) and "Water" not in G[rm.y + y, rm.x + x]
                     and O[rm.y + y, rm.x + x] is None and "Edge" not in G[rm.y + y, rm.x + x]]
            rng.shuffle(cells)
            fixed_mon = sum(1 for y in range(rm.h) for x in range(rm.w) if O[rm.y + y, rm.x + x] in enemy) if rm.tmpl else 0
            fixed_prop = sum(1 for y in range(rm.h) for x in range(rm.w)
                             if O[rm.y + y, rm.x + x] and O[rm.y + y, rm.x + x] not in enemy
                             and "Wall" not in O[rm.y + y, rm.x + x]) if rm.tmpl else 0
            for key, count in (("mon", max(0, rng.choice(pop["mon_n"]) - fixed_mon)),
                               ("prop", max(0, rng.choice(pop["prop_n"]) - fixed_prop))):
                FIXED = ("Dreadstump the Pirate King", "PC Dreadstump Cannon")   # come from the boss ship template
                items = [(n, v) for n, v in pop[key].items() if n not in FIXED]
                names, wts = [n for n, v in items], [v for n, v in items]
                if not names:
                    continue
                for _ in range(count):
                    if not cells:
                        break
                    x, y = cells.pop()
                    O[y, x] = rng.choices(names, wts)[0]

    def populate_water(self, G, O):
        P, rng = self.P, self.rng
        names, wts = list(P["wprops"].keys()), list(P["wprops"].values())
        if not names:
            return
        cells = [(x, y) for y in range(SIZE) for x in range(SIZE) if "Water" in G[y, x] and O[y, x] is None]
        rng.shuffle(cells)
        for _ in range(min(rng.choice(P["wprops_n"]), len(cells))):
            x, y = cells.pop()
            O[y, x] = rng.choices(names, wts)[0]

    def export(self, G, O):
        dct, look = [], {}
        grid = []
        for y in range(SIZE):
            for x in range(SIZE):
                e = {"ground": G[y, x]}
                if O[y, x]:
                    e["objs"] = [{"id": O[y, x]}]
                k = json.dumps(e, sort_keys=True)
                if k not in look:
                    look[k] = len(dct); dct.append(e)
                grid.append(look[k])
        return {"name": "Pirate Cave (generated)", "width": SIZE, "height": SIZE, "dict": dct, "grid": grid}

def generate(P, seed):
    for attempt in range(200):
        g = Gen(P, "%s:%d" % (seed, attempt))
        if g.run():
            G, O = g.raster()
            g.populate(G, O)
            g.populate_water(G, O)
            m = g.export(G, O)
            m["seed"] = seed
            m["attempts"] = attempt + 1
            return m
    raise RuntimeError("no map for seed %s" % seed)

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "gen"
    if cmd == "params":
        build_params(); return
    P = json.load(open(PARAMS))
    os.makedirs(GEN, exist_ok=True)
    if cmd == "gen":
        from PIL import Image
        from pc_classes import COL
        for s in sys.argv[2:] or ["1"]:
            m = generate(P, int(s))
            json.dump(m, open(os.path.join(GEN, "pc_%s.json" % s), "w"), separators=(",", ":"))
            w, h, cls = classes(m)
            img = Image.new("RGB", (w * 6, h * 6))
            px = img.load()
            for i, c in enumerate(cls):
                x, y = i % w, i // w
                for dy in range(6):
                    for dx in range(6):
                        px[x * 6 + dx, y * 6 + dy] = COL[c]
            img.save(os.path.join(ROOT, "maps", "png", "pc_gen_%s.png" % s))
            print("seed", s, "attempts", m["attempts"])
    elif cmd == "compare":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        stats = []
        for s in range(1000, 1000 + n):
            m = generate(P, s)
            path = os.path.join(GEN, "tmp_%d.json" % s)
            json.dump(m, open(path, "w"), separators=(",", ":"))
            r = pc_rooms.extract(path)
            for rm in r["rooms"]:
                rm["kind"] = pc_rooms.kind(rm)
            tmp = os.path.join(ROOT, "rooms", "pirate_cave", "tmp_gen_%d.json" % s)
            json.dump(r, open(tmp, "w"))
            stats.append(pc_graph.analyze(tmp))
            os.remove(path); os.remove(tmp)
        real = json.load(open(os.path.join(ROOT, "rooms", "pirate_cave_stats.json")))
        def summ(name, L):
            rooms = [a["rooms"] for a in L]; loops = [a["loops"] for a in L]; hops = [a["hops"] for a in L]
            off = [a["off_path"] for a in L]; bd = [a["branch_depth_max"] for a in L]
            kinds = Counter(k for a in L for k, v in a["kinds"].items() for _ in range(v))
            print("%-10s rooms %s-%s mean %.1f | loops %s | hops %s | off-path %s-%s | max branch depth %s-%s mean %.1f"
                  % (name, min(rooms), max(rooms), sum(rooms) / float(len(L)), sorted(set(loops)), sorted(set(hops)),
                     min(off), max(off), min(bd), max(bd), sum(bd) / float(len(L))))
            print("           kinds per map:", {k: round(v / float(len(L)), 1) for k, v in kinds.items()})
        summ("real", real); summ("generated", stats)

if __name__ == "__main__":
    main()
