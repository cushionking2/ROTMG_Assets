# The Hive

Source files: The Hive - the RotMG Wiki _ RealmEye.com.html; The Hive Guide - the RotMG Wiki _ RealmEye.com.html

## Overview
- Portal / how to enter: The portal always drops from Warrior Bees, Wasp Queens and Legion Surveyor. Warrior Bees and Wasp Queens live in the Mid Plains. The key costs 50 in the Nexus.
- Theme and setting: A bee colony. The bees made a pact with Oryx to produce honey and mead. Rooms have yellow honeycomb floors and dark yellow waxy walls.
- Party size, difficulty, level range: Low-level, community-made dungeon for level 10+ characters. The guide says it is fairly difficult for the early game. It recommends at least T3 armor and weapon. Party size is not given. A harder version exists: The Nest.
- Time or wave limits, if any: None. Once the dungeon is fully cleared, enemies stop respawning.

## Layout and map logic
- Overall structure (rooms, corridors, open cave, grid, linear): Irregular circular rooms joined by short hallways. The guide calls it somewhat maze-like. It is easy to reach the boss by following the quest marker.
- Room sizes and counts, if the guide gives them: The wiki guesses exactly 6 rooms including the boss, but says this is unconfirmed. Rooms can fuse. One run had the spawn room fused to the boss room.
- Special mechanics (keys, doors, waves, hazards, puzzles, destructible walls): Honey sits on room edges and between rooms. It does no damage. It slows players more the longer they stand in it, like quicksand in Ancient Ruins. Mini Hives spawn Small Bees and Fat Bees and always drop Bottled Honey. Maggots become Fat Bees after exactly 10 seconds. Fat Bees sometimes become Fat Angry Bees on death. Maggot Eggs come from the boss.
- Order of progress (rooms, minibosses, boss): Rooms of bees and Mini Hives, then Queen Bee. Destroy Mini Hives first when clearing.
  - Queen Bee: black bolts around her (short range), then a red bomb (heavy damage). Then she chases the closest player with bursts of 3 honey shots that Daze. Then another red bomb. The cycle repeats. She throws bombs that spawn Maggot Eggs. She is Invulnerable between phases and moves erratically. The guide says two phases.

## Enemies
| Name | Role (regular / miniboss / boss) | Key attacks or behavior | Notes |
|---|---|---|---|
| Small Bee | regular | Erratic; hits hard for size | From Mini Hives |
| Fat Bee | regular | Erratic; fairly high damage | From Mini Hives and Maggots |
| Fat Angry Bee | regular | Less damage; Bleeding | Sometimes spawns when a Fat Bee dies |
| Mini Hive | spawner (stationary) | Spawns Small and Fat Bees | Guaranteed Bottled Honey drop; usually in room center; rare |
| Maggot Egg | spawned object | Breaks into Maggots | Spawned by the boss |
| Maggot | regular | Slowing effect | Becomes Fat Bee after 10 s |
| Honey | hazard | Slows | |
| Queen Bee | boss | See above | |
| Warrior Bee, Wasp Queen, Legion Surveyor | outside portal droppers | | Mid Plains |

## Tiles and objects to find as sprites
- Floor tiles: Yellow honeycomb floor. Honey liquid tiles.
- Wall tiles: Dark yellow waxy walls.
- Hazards and props: Honey puddles, Mini Hives, Maggot Eggs.
- Other objects (chests, portals, doors, keys): Hive portal and key. Boss loot bags.

## Loot
- Queen Bee drops: Honey Scepter, Orb of Sweet Demise, small chance of Potion of Dexterity, Bee Egg (becomes a Bee Pet Skin).
- Bottled Honey (Healing for a short time) drops from Mini Hives and the boss. It is exclusive to the Hive.
- Completion gives Travel of the Decade, First Steps, Hero of the Nexus and Realm of the Mad God fame bonuses. The page shows "6-11" under Dust Drops, with the label lost.

## Sprite search hints
- Words to search in `Objects.xml` and `GroundTypes.xml`: Hive, Bee, Queen Bee, Fat Bee, Angry Bee, Mini Hive, Maggot, Maggot Egg, Honey, Honeycomb, Wax, Wasp.

## Gaps
- Confirmed room count and room sizes.
- HP and defense values.
- Which honey tiles exist as separate ground types.
- Item names in the drop table were images and are lost.
- Mini Hive and bee counts per room.
