# Dungeon pipeline: from packets to a generator

This document explains how we turn live game traffic into data that a dungeon generator can use.
It covers the setup, each step, the file formats, the results for Pirate Cave, and the known limits.
Build tested: Realm of the Mad God Exalt 7.2.0.1.0. Date: 2026-11-21.

## 1. Why we use packets

- The dungeon layout is not in the game files. The server builds each dungeon.
- The server sends the finished tiles and objects to the client. The client draws them.
- The generator code never reaches your machine. We can see only the result.
- So the plan is: record many finished dungeons, measure the rules, and write our own generator.
- The generator copies the **style and statistics** of the real dungeon. It does not copy the server code.
- Old server code from the Flash era does not match the current game. We deleted it. We use current captures only.

## 2. Data flow

```
 Game client <--TCP port 2050--> Game server
        |
   (Npcap copies the packets)
        v
 RealmShark library  (decrypts and decodes packets)
        v
 collector/MapCollector.java
        v
 collector/captures/<time>_<map>.jsonl           map: size, tiles, objects
 collector/captures/<time>_<map>.events.jsonl    behavior: ticks, shots, damage, text, loot
        v  tools/capture_to_map.py            (ids -> names, via work/objects.json)
 maps/live/<time>_<map>.json                     one grid per dungeon run
        v  tools/render_tiles.py / jm_render.py (pictures)
 maps/png/*.png
        v  tools/pc_rooms.py, pc_graph.py       (rooms, corridors, room graph)
 rooms/pirate_cave/*.json, rooms/pirate_cave_stats.json
        v  tools/pc_gen.py params               (measure parameters)
 rooms/pirate_cave_params.json
        v  tools/pc_gen.py gen <seed>
 maps/generated/pc_<seed>.json   --> tools/render_tiles.py --> picture

 Events: collector/*.events.jsonl --tools/analyze_events.py--> behaviors/<time>_<map>.md and .json
```

## 3. Setup (one time)

1. Install Npcap from https://npcap.com/#download. Use the default options.
2. The JDK 17 is in `work/jdk`. The Java libraries are in `collector/lib`. The RealmShark source is in `research/X-com_RealmShark`.
3. Build the collector: run `collector\build.bat`. Run it again only after you change `collector/src/MapCollector.java`.
4. Python needs `numpy` and `Pillow`. Run scripts with `python -I`.

RealmShark is a passive sniffer. It cannot send, block or change packets.

## 4. Capture

1. Run `collector\run.bat`. Wait for `Map collector started`.
2. Enter the dungeon. Start the collector first.
3. Walk the whole dungeon. The server sends only the tiles near you.
4. Fight enemies and the boss to record behavior.
5. Check the `[status]` line (every 10 seconds). `packetTypes`, `tiles` and `events` must grow.
6. Leave the dungeon. The console prints `[closed]`. Close the window with Ctrl+C when you finish.

The collector skips `Nexus` and `Realm of the Mad God`. To skip more maps, edit `SKIP` in `MapCollector.java`
and in `tools/capture_to_map.py` and `tools/analyze_events.py`, then rebuild.

Capture advice:
- Capture each dungeon at least 8 to 10 times. Layouts are random.
- Do not run two game clients. RealmShark cannot separate them.
- Check completeness with the render, not with a "coverage" number. A map is cut off only if a room shows a straight edge.

## 5. Convert

```
python -I tools/capture_to_map.py        # maps/live/*.json
python -I tools/analyze_events.py        # behaviors/*.md and *.json
python -I tools/render_tiles.py maps/live/<file>.json --px 16
```

`capture_to_map.py` turns tile and object ids into names. It reads `work/objects.json`, which comes from the game XML.
All Pirate Cave ids resolved to names. If an id has no name, the file says `unknown_0x...` and the stats show `unknown_tile_ids`.

## 6. File formats

**Capture map file** (`.jsonl`, one JSON object per line)
- Line 1: `{"kind":"mapinfo", name, width, height, seed, version, modifiers, grade, raw}`.
- Next lines: `{"kind":"update", tiles:[[x,y,groundId]...], objs:[[objectId,type,x,y]...], drops, raw}`.
- `raw` holds the decrypted packet in base64. Use it to re-decode if the format changes.
- The `seed` field is the library's `fp` value. It may be a seed. We did not confirm that.

**Capture events file** (`.events.jsonl`, field `k` is the event type)
`tick`, `upd`, `eshoot`, `dmg`, `aoe`, `fx`, `text`, `notif`, `goto`, `quest`, `self`, `pshoot`.
Stats are `[statNumber, value]`. Stat 0 is max HP, 1 is HP, 29 is condition, 31 is name, 8 to 19 are inventory slots.

**Live map file** (`maps/live/*.json`)
`{name, seed, width, height, dict, grid, stats}`. `dict` is a list of `{"ground": name, "objs": [{"id": name}]}`.
`grid` has `width*height` indexes into `dict`, row by row. A tile that the server never sent is `{"ground": "Space"}`.

**Room file** (`rooms/pirate_cave/*.json`)
`rooms`: id, x, y, w, h, area, fill, kind, monsters, props. `corridors`: tiles, w, h, and the room ids each one touches.

## 6A. Object IDs, duplicates and moving enemies

- Every object (enemy, wall, prop, loot bag) has an **object id**. The id is unique inside one dungeon run. A new run gives new ids.
- The server sends an object in an update each time it enters your view. If you walk away and come back, it is sent again with the same id.
  Measured on one Pirate Cave run: 4,169 sightings, 1,520 unique objects. For enemies: 213 sightings, 135 unique.
- `capture_to_map.py` keeps **one entry per object id**, at the first position it was seen. Before 2026-11-21 it keyed by tile instead.
  That inflated enemy counts by about 50% (224 vs 149 per map) and dropped objects when two shared a tile. This is fixed.
- The map file puts all objects of a tile in the `objs` list. Static objects (walls) come first.
- An enemy that moves is **not duplicated**: its id stays the same. Its map position is only where it was first seen.
  On one run, 52 of 126 enemies ended more than 3 tiles from the first-seen position (median 2.5, max 20 tiles).
- For true spawn positions, use the events file: `upd` gives the first position, `tick` gives later positions by id.
- `analyze_events.py` counts by object id, so its enemy counts are unique.
- Unique enemies per Pirate Cave map: 135 to 182 (mean 149).
- A tick lists only objects whose position or stats changed. An enemy that never moves and never takes damage is in no tick.
  Measured on 9 Pirate Cave runs: 82 of 1,350 enemies (6.1%) were in no tick. 81 were `PC Dreadstump Cannon` (stationary, invincible).
  The other one was a Pirate Lieutenant that left view first. So "no tick" means "stationary", not "missing".
- Cannon activation (Pirate Cave boss ship): the 9 cannons are in no tick in any of 9 runs, even when they fire. Their shots show in `eshoot` events.
  They fired in 5 of 9 runs (9 to 56 shots) and never in 4 runs. The 4 silent runs had the shortest boss fights (48 to 58 s from first sighting
  to last boss tick, against 67 to 106 s). The user suggested a fast boss kill stops the cannons. The data fits this.
  Trigger (tool: `tools/pc_cannon_trigger.py`): the cannons start about 3 to 4 s after the boss HP drops below about half (max HP 1000; 1150 in one run).
  Evidence: in 3 runs the boss HP stayed at 525, 537 or 608 for several seconds with no cannon shot, so the trigger is below those values.
  In run 21:34 the HP stayed at 373 and the cannons fired, so the trigger is above 373. The range 373 to 525 fits 50 percent.
  In the 4 silent runs the boss died within 1 s of dropping below 50 percent. HP samples are sparse and ticks list only changes,
  so this is a fit to 9 runs, not a proof. The delay is estimated from 5 runs.
- Generator parameters (`pc_gen.py params`) now use the de-duplicated maps. Floating props on the water are included.

## 7. Room extraction

Script: `tools/pc_rooms.py`. Classes come from `tools/pc_classes.py`.

1. Class each tile: water, sand, wood floor, carpet, cave wall, wood wall, torch wall, void.
2. Build a mask of structure tiles (sand, wood, carpet, walls). Fill small enclosed water pools, so a cabin stays one room.
3. Erode the mask by 2 tiles. Thin planks (2 wide) disappear. Each remaining blob is a room core.
4. Grow each core back into the mask. The rest of the mask is corridors (planks).
5. Name each room: `boss_ship` (carpet), `cabin` (torch walls), `small_ship`, `island` (sand), `deck`.
6. Build the room graph from the corridors. `tools/pc_graph.py` measures path length, loops and branch depth.

Use `tools/pc_debug_render.py <map>` to draw room ids on a map. Check the result by eye. The fill step was found this way.

## 8. Results for Pirate Cave (10 captures)

| Fact | Value |
|---|---|
| Grid | 128 x 128 |
| Rooms per map | 16 to 19 (mean 17.7) |
| Graph | One tree. No loops in 10 of 10 maps. |
| Spawn to boss | Always 5 corridor hops |
| Rooms off the main path | 10 to 13, up to 6 rooms deep |
| Spawn room | Fixed sand circle, 20 x 20 |
| Boss ship | Fixed template, 41 x 21, carpet circle, Dreadstump the Pirate King, cannons |
| Octagon cabin | Fixed template, 17 x 13, torch walls, water pool. Plays like a normal room (user). |
| Small ships | 23 x 13 and 13 x 25. In 3 of 10 maps. |
| Islands | Circles, diameter 13 to 18, 1 to 3 per map |
| Decks | Wood rectangles, 5 to 12 wide, 6 to 12 tall |
| Gap between linked rooms | 4 to 7 tiles. Planks are 2 tiles wide. |
| Water bay | Water up to 4 tiles from any structure. Cave wall at 5. |

More detail: `docs/pirate_cave_findings.md`.

## 9. The generator

Script: `tools/pc_gen.py`.

```
python -I tools/pc_gen.py params         # measure rooms/pirate_cave_params.json from the captures
python -I tools/pc_gen.py gen 5 6 7      # maps/generated/pc_<seed>.json and a class picture
python -I tools/pc_gen.py compare 60     # compare generated and real statistics
python -I tools/render_tiles.py maps/generated/pc_5.json --px 16   # picture with real sprites
```

Method:
1. Make the main path: spawn island, 4 rooms, boss ship. Retry with backtracking if rooms collide.
2. Add side rooms until the total matches a measured count. A new room extends the newest branch with probability 0.33. Branches stop at depth 6.
3. Place each room 4 to 7 tiles from its parent. Join them with a 2-wide plank. Reject any room that overlaps another or leaves the 128 x 128 grid.
4. Copy fixed templates from the captures. Draw islands and decks from measured sizes and floor patterns.
5. Add the water bay and the cave wall. Add monsters and props, sampled from measured counts and species.

Comparison (60 generated maps against 10 real maps): room count, 5 hops, no loops, 10 to 13 off-path rooms and branch depth 3 to 6 all match.

## 10. Known limits

- 10 captures is a small sample.
- Monsters and props are sampled from measured counts. They do not follow a measured placement rule. Counts match real maps (monsters 140 vs 149, props 298 vs 304).
- Enemy positions are first-seen positions. About 40% of enemies move more than 3 tiles from there (see section 6A).
- The vertical-wood deck pattern is a guess.
- The first room after the spawn is placed freely. Real maps may restrict it.
- The sprite render matches by name. We did not compare it tile by tile with a real capture.
- The behavior data is only lightly tested. Speeds look quantized. The value 255 in shots per volley probably means one shot.
- Boss phases need long fights. Most enemies died too fast to show phases.
- We cannot recover the server algorithm or seed. We copy the style only.

## 11. Add another dungeon

1. Capture the dungeon 8 to 10 times. Run `capture_to_map.py` and `render_tiles.py`. Look at the pictures.
2. Copy `pc_classes.py`, `pc_rooms.py` and `pc_graph.py`. Change the tile classes to fit the new dungeon.
3. Run the extraction. Open the debug render. Fix the room splits.
4. Measure: room count, room kinds and sizes, path length from spawn to boss, loops, branch depth, gaps, fixed templates.
5. Ask the player what they know. We used this for the spawn room and the cabin.
6. Copy `pc_gen.py`. Replace the parameters. Run `compare`. Tune until the statistics match.

Dungeons seen in captures so far: Pirate Cave (10), The Hive (4), Forest Maze (3), Snake Pit (2), Spider Den (2), Magic Woods (2).
Snake Pit and Spider Den are round rooms joined by corridors, so the Pirate Cave code may need only a new tile set and room shapes.

## 12. Troubleshooting

| Problem | Action |
|---|---|
| `packetTypes` stays 0 | The sniffer sees no game traffic. Check Npcap. Start the collector before the game. |
| `tiles` stays 0 but packets arrive | The packet format changed. Use the `raw` field to re-decode. Update the RealmShark source. |
| Collector crashes at start | One JVM crash happened at 0.4 seconds (`collector/hs_err_pid8600.log`). A second start worked. Run it again. |
| Two or more Realm or Nexus files | They are skipped now. Old ones were deleted. |
| `KeyError: 'kind'` in `capture_to_map.py` | A script read an events file. Fixed: the script skips `.events.jsonl`. |
| Names show `unknown_0x...` | The game was updated. Rebuild `work/objects.json` (see `docs/EXTRACTION_PLAN.md`). |

## 13. Tool list

| Tool | Job |
|---|---|
| `collector/src/MapCollector.java` | Record maps and events from packets |
| `tools/capture_to_map.py` | Captures to named map grids |
| `tools/analyze_events.py` | Enemy behavior summaries |
| `tools/jm_render.py` | Quick class-color previews of live maps |
| `tools/render_tiles.py` | Pictures with real sprites (full map or crop) |
| `tools/pc_classes.py`, `pc_rooms.py`, `pc_graph.py`, `pc_debug_render.py` | Pirate Cave room extraction and graph stats |
| `tools/pc_gen.py` | Pirate Cave generator and comparison |
