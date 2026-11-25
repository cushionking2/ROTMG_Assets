# Pirate Cave: findings from live captures (build 7.2.0.1.0)

Source: 10 captures in `maps/live/*Pirate_Cave.json`. Rooms extracted by `tools/pc_rooms.py` into `rooms/pirate_cave/`.
All numbers below are measured from those 10 maps. The sample is small.

## Structure
- Map grid is 128 x 128. The cave is a water bay with a cave wall on the outside edge.
- Rooms are separate pieces joined by thin wooden planks (2 to 3 tiles wide).
- Room count: 16 to 21 per map (median 20). Decks (wood rooms) 11 to 17. Sand islands 2 to 4. Boss ship always 1.
- The room graph is one connected tree, with 0 to 2 extra loops. Leaf rooms: 5 to 9 per map.
- **Spawn to boss is exactly 5 corridor hops in all 10 maps.** This looks like a fixed main-path depth.
- Boss ship is not always far in tiles (39 to 94 tiles apart). It is always far in hops.

## Room types
| Type | Size (tiles) | Notes |
|---|---|---|
| Boss ship | 41 x 21, all 10 maps | Fixed template. Arrow shape, carpet circle. 24 to 52 monsters. Dreadstump the Pirate King, cannons, admiral, captain, lieutenant. |
| Spawn island | 20 x 20 sand circle, all 10 maps | User confirmed: spawn is here. |
| Other islands | circles of diameter 13 to 18 | 1 to 3 per map. Median 11 monsters. Palm trees, flags, sand castles, anchors. |
| Octagon cabin | 9 x 8, 16 times | Torch walls and a water pool. User says it plays like a normal room. |
| Deck | rectangles, 5 to 12 wide, 6 to 12 tall | Common sizes 9x8 (16), 5x8 (15). Crates, vases, barrels, paintings. Median 8 monsters. |
| Irregular deck | 23x13, 13x25 | Probably two or three decks that touch. Needs a split rule. |

## User answers (2026-11-21)
- Spawn room is the 20-wide island.
- Octagon cabin is a normal room.
- Boss is far from spawn. Several routes exist. Rooms form one long chain with side branches.

## Open questions
- Do all decks with the same size use one template (for example 5x8 and 9x8)?
- What decides how many side rooms appear (10 to 13 off the main path)?
- The user remembers several routes to the boss. The data shows one route (0 loops in 10 maps). Capture more runs to check.

## Corrections after review (2026-11-21)
- Loops: 0 in all 10 maps. Earlier loops came from cabins split by their water pool. Rooms are a pure tree.
- Cabin is 17 x 13 (octagon with torch walls and a water pool). Small ships exist: 23 x 13 and 13 x 25, in 3 of 10 maps.
- Fixed templates (identical across maps apart from decor walls): boss ship 41x21, cabin 17x13, small ships, spawn island 20x20.
- Gap between linked rooms: 4 to 7 tiles (mostly 4 to 6). Plank width 2. Unlinked rooms can sit 1 tile apart.
- Water bay reaches 4 tiles from any structure, cave wall at 5 tiles. Water shade depends on distance (bright near shore, dark far).
- Deck floor: edge rows (Edge L / Edge R) on the two long sides, about a quarter of interior tiles cracked.

## Generator: `tools/pc_gen.py`
`python -I tools/pc_gen.py params | gen <seeds> | compare <n>`. Output: `maps/generated/pc_<seed>.json` and `maps/png/pc_gen_<seed>.png`.
Comparison with the 10 real maps (60 generated): rooms 16-19 (mean 17.4 vs 17.7), hops always 5, loops 0,
off-path rooms 10-13, max branch depth 3-6 (mean 4.5 vs 4.5), room kinds per map close.
Counts after de-duplicating by object id: monsters 140 vs 149 real, props 298 vs 304. Known gaps: vertical-wood deck pattern is a guess; monster and prop placement is sampled, not rule-based;
the first room after spawn is placed freely (real maps may restrict it); no check yet of bay shape details or the tile-level look of planks at room edges.
