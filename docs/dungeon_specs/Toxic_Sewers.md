# Toxic Sewers

Source files: Toxic Sewers - the RotMG Wiki _ RealmEye.com.html; Toxic Sewers Guide - the RotMG Wiki _ RealmEye.com.html

## Overview
- Portal / how to enter: The portal has a chance to drop from Noxious Sprite (Sprite Forest), Smelly Octopus (Coral Reefs), Brimstone Wyvern (Risen Hell), Slime God (Abandoned City) and Eternal Tormentor. The guide says the rate is moderate to low. The key costs 50 in the Nexus.
- Theme and setting: An old drainage system left without maintenance after Oryx took power. Sickly sewers are home to reviled creatures. Music: Virulent. Players made the dungeon (designer: Kiddforce). It was first called "Dank Sewer".
- Party size, difficulty, level range: Medium-level, community-made. The guide recommends level 20 and maxed Speed. The guide calls it a decently challenging midgame dungeon. A party of 2 is guaranteed a Potion of Defense each.
- Time or wave limits, if any: None given. The Golden Rat despawns after about 15 seconds.

## Layout and map logic
- Overall structure (rooms, corridors, open cave, grid, linear): A network of narrow corridor rooms with some branches and larger rooms. The guide compares it to Manor of the Immortals: long hallways, large rooms, occasional four-way splits. Path count is random. The minimap shows the boss location.
- Room sizes and counts, if the guide gives them: 8-10 rooms between spawn and boss. L-shaped and U-shaped rooms count as one room. Two flowing-water rooms joined by a narrow passage count as one. The start and treasure rooms are small and square. The boss room is a large rounded square, mostly Sludge, with a square walkway in the center. A split holds at most 3 rooms.
- Special mechanics (keys, doors, waves, hazards, puzzles, destructible walls):
  - Sludge inflicts Sick when players stand on it. Sick lasts a few seconds after leaving. Sick stops HP regeneration. Most rooms have a Sludge river in the center and normal tiles at the edges. Some rivers flow and push players.
  - Water in the narrow hallways between rooms does not cause Sick.
  - Floors: dark gray tiles, sludge-stained tiles (no Sick), grated walkways. Walls: gray bricks. Machinery operates in some sludge pools.
  - A rare treasure room holds the Master Rat. Its chance is much lower than in other dungeons. A Golden Rat may appear in any normal room (uncommon, more common than the treasure room). It says "Squeek!" in chat.
  - Walking on the boss room grating activates Gulpord. Walking in the sewage at the edge does not.
- Order of progress (rooms, minibosses, boss): Spawn, 8-10 rooms, boss room.
  - Gulpord phase 1: 5-armed tentacle rotation of small brown shots with occasional rings of green Slowed shots. Then he circles counterclockwise, firing a 3-wide shotgun and rapid lingering shots opposite the player. Lasts until about 40% HP.
  - Phase 2: Invulnerable, he sinks and splits into 2 smaller Gulpords in the East and West pools. Each fires a clockwise 4-armed spiral, then half-rings of shots with gaps 45 degrees toward the player.
  - Phase 3: The 2 clones split into 4 smaller ones in the 4 cardinal directions of the center. They rotate counterclockwise firing single rapid shots in and out. Then they move to the outer pools (north, east, west, south order).
  - Phase 4: All clones rejoin as Gulpord in the center. He chases the nearest player with the 3 shot spread, a rapid backward shot and rings of accelerating green Slowing shots. He flashes red, is immune to stun, and throws armor break stars.
  - Damage to the split Gulpords does not count for soulbound damage.

## Enemies
| Name | Role (regular / miniboss / boss) | Key attacks or behavior | Notes |
|---|---|---|---|
| Goblin Brute | regular | Charges; short-range high-damage shotgun | Can kill non-maxed-defense classes in seconds; triple-digit DPS on unmaxed |
| Goblin Knight | regular | Charges; one weaker shot | Drops items |
| Goblin Peon | regular | Charges; armor-piercing shots | |
| Goblin Sorcerer | regular | Silence shots | Low damage |
| Goblin Warlock | regular | 3 rapidly accelerating shots | Drops items |
| Natural Slime God | regular (strong) | Predicts player movement; shotgun; Slowing green star | Higher Defense potion chance; 3 or 4 guard the boss (see Gaps) |
| Sewer Alligator | regular | Fast; heavy damage; charges | Drops items |
| Sewer Bat | regular | Low damage; Sick for 3 s | |
| Sewer Brown Slime | regular | Slime Trails that Silence | Drops items |
| Sewer Yellow Slime | regular | Harder shots and trail; no Silence | Drops items |
| Sewer Rat | regular | Pattern like Warlock, not accelerating | |
| Sewer Dummy | regular/prop | Not described | In treasure room (training dummies) |
| Golden Rat | special encounter | Runs from nearest player; despawns in about 15 s | Drops Potion of Defense, Murky Toxin |
| Master Rat | treasure room boss | See phases below | Holds a Void Blade |
| Gulpord the Slime God | boss | See above | |
| Sludge | hazard | Sick | |
| Noxious Sprite, Smelly Octopus, Brimstone Wyvern, Slime God, Eternal Tormentor | outside portal droppers | Noxious Sprite: shotgun plus a Silencing side shot | |

Master Rat fight: phase 1 circles the center and leaves delayed accelerating Void Stars. Phase 2 (after about a third of HP is lost) circles faster and wider, with four decelerating Void Slashes. Phase 3 (one third HP) circles fast near the edges with non-stop Void Slashes. At 1 HP he turns invulnerable and spawns a box with a Potion of Defense, a chance at Power Pizza and a chance at the Void Blade. He has taunt lines. Four colored turtles appear after his defeat.

## Tiles and objects to find as sprites
- Floor tiles: Dark gray tiles, sludge-stained tiles, grated walkways, Sludge (flowing and still).
- Wall tiles: Gray brick walls.
- Hazards and props: Sludge, machinery in sludge pools, boss room grate, training dummies, turtles, loot box, Slime Trails.
- Other objects (chests, portals, doors, keys): Toxic Sewers portal and key. Boss loot bags. Treasure room.

## Loot
- Potion of Defense from the boss, Master Rat and Golden Rat. Natural Slime Gods may drop one.
- Untiered: Murky Toxin, Void Blade. Acidified Assassin set: Toxin Tooth, Virulent Venom, Acidic Armor, Pernicious Peridot.
- Slurp Knight Skin (boss, chance). Turtle Pet Skin (boss and Master Rat). Power Pizza (Master Rat box, chance).
- Completion gives Travel of the Decade, King of the Mountains, Hero of the Nexus and Realm of the Mad God fame bonuses. The page shows "33-39" under Dust Drops, with labels lost.

## Sprite search hints
- Words to search in `Objects.xml` and `GroundTypes.xml`: Sewer, Sludge, DS (Dank Sewer prefix), Dank, Gulpord, Slime God, Natural Slime God, Goblin Brute, Goblin Knight, Goblin Peon, Goblin Sorcerer, Goblin Warlock, Alligator, Sewer Bat, Brown Slime, Yellow Slime, Sewer Rat, Golden Rat, Master Rat, Turtle, Dummy, Grate, Machinery.

## Gaps
- Pixel sizes of rooms and the boss room.
- HP and defense values.
- Slime God count in the boss room: the Tips section on the main page says three, the Guide says four.
- Exact ground type names for Sludge variants.
- Item names in the drop tables were images and are lost.
- Sewer Dummy behavior.
