"""Room graph statistics for Pirate Cave (from rooms/pirate_cave/*.json).
Run: python -I tools/pc_graph.py  -> prints stats and writes rooms/pirate_cave_stats.json
"""
import glob, json, math, os
from collections import defaultdict, deque, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def graph(r):
    rooms = {x["id"]: x for x in r["rooms"]}
    adj = defaultdict(set)
    edges = set()
    for c in r["corridors"]:
        rs = [i for i in c["rooms"] if i in rooms]
        for a in rs:
            for b in rs:
                if a < b:
                    edges.add((a, b)); adj[a].add(b); adj[b].add(a)
    return rooms, adj, edges

def bfs(adj, s, blocked=()):
    d = {s: 0}; par = {s: None}
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in d and v not in blocked:
                d[v] = d[u] + 1; par[v] = u; q.append(v)
    return d, par

def analyze(path):
    r = json.load(open(path))
    rooms, adj, edges = graph(r)
    spawn = [i for i, x in rooms.items() if x["kind"] == "island" and x["w"] >= 20][0]
    boss = [i for i, x in rooms.items() if x["kind"] == "boss_ship"][0]
    d, par = bfs(adj, spawn)
    path_ids = []
    u = boss
    while u is not None:
        path_ids.append(u); u = par[u]
    path_ids.reverse()
    on = set(path_ids)
    # branch depth: distance from the main path
    dist = {n: 0 for n in on}
    q = deque(on)
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1; q.append(v)
    comps = 0; seen = set()
    for n in rooms:
        if n not in seen:
            comps += 1; seen |= set(bfs(adj, n)[0])
    cx = lambda x: (x["x"] + x["w"] / 2, x["y"] + x["h"] / 2)
    return {
        "file": r["file"], "rooms": len(rooms), "edges": len(edges), "loops": len(edges) - len(rooms) + comps,
        "components": comps, "hops": d[boss], "path_kinds": [rooms[i]["kind"] for i in path_ids],
        "off_path": len(rooms) - len(on), "branch_depth_max": max(dist.values()),
        "branch_depths": dict(Counter(v for k, v in dist.items() if v > 0)),
        "degree": dict(Counter(len(adj[n]) for n in rooms)),
        "spawn_boss_tiles": round(math.dist(cx(rooms[spawn]), cx(rooms[boss]))),
        "kinds": dict(Counter(x["kind"] for x in rooms.values())),
    }

if __name__ == "__main__":
    out = [analyze(f) for f in sorted(glob.glob(os.path.join(ROOT, "rooms", "pirate_cave", "2*.json")))]
    for a in out:
        print(a["file"][:15], "rooms", a["rooms"], "loops", a["loops"], "hops", a["hops"], "off-path", a["off_path"],
              "branch depth", a["branch_depths"], "path", "/".join(k[0] for k in a["path_kinds"]))
    json.dump(out, open(os.path.join(ROOT, "rooms", "pirate_cave_stats.json"), "w"), indent=1)
