# Woodland Labyrinth

Source files: Woodland Labyrinth - the RotMG Wiki _ RealmEye.com.html; Woodland Labyrinth Guide - the RotMG Wiki _ RealmEye.com.html

## Overview
- Portal / how to enter: The portal always drops from Possessed Pumpkin (Haunted Hallows) and Legion Head Researcher. It has a chance to drop from Man-Eating Flytrap (Carboniferous), Great Owl (Floral Escape), Hornet's Nest and Bloodroot Treant (Sanguine Forest). The key costs 100 in the Nexus.
- Theme and setting: A dense highland forest, like the Forest Maze. Plants eject matter at bullet speed. Megamoths made the jungle feared.
- Party size, difficulty, level range: High-level. It is a much harder Forest Maze. The guide recommends maxed ATT, DEF, SPD and DEX. Party size is not given. The first "Epic Dungeons" group (Aug 2013, Release 16.0.0).
- Time or wave limits, if any: None given.

## Layout and map logic
- Overall structure (rooms, corridors, open cave, grid, linear): Rooms in a dense forest. Each room is a random premade setpiece. The layout is procedurally generated. Floors are grass with some exposed dirt. Trees act as walls. Rooms join by dark pathways between trees. The pathways do not show on the minimap but show as openings if the camera rotates. Enemies can hide in covered corridors and show only as minimap dots.
- Room sizes and counts, if the guide gives them: No numbers are given. One room type is shaped like the Honey Scepter (easter egg).
- Special mechanics (keys, doors, waves, hazards, puzzles, destructible walls):
  - Invincible plant turrets in each room inflict Paralyzed, Silenced or Weak.
  - One treasure room always spawns, never more than one. It sits at the end of a long pathway in the trees (a longer-than-usual corridor).
  - Puke Water (boss room) lasts to the end of the fight. It does about 20 damage per tick (marked "needs confirmation") and inflicts Sick. Woodland Water is also an environmental hazard.
  - A rare destructible object (Woodland Skysplitter Stone) can drop the Blessed Blade Pet Skin.
- Order of progress (rooms, minibosses, boss): Rooms, then treasure room (optional), then the boss room.
  - Phase 1, Megamoth Larva: up to 4 Mini Larvae. 8-bullet bursts of green Sick spirals. Chases players with a 3-armed spiral of blue missiles. After some time or at 1 HP it goes to the center, flashes red, throws Larva Puke and turns invulnerable.
  - Phase 2, Mammoth Megamoth: up to 5 minions. Mini Larvae evolve into Micro Megamoth Sentinels (Confused; the guide says Unstable). Pattern A: moves between corners, converging green bolts. Pattern B: circles the edge, 2 perpendicular barrages (Stunning green crescents per guide). Special at about half HP: from the center, 4-way barrages of white shots that alternate cardinal and diagonal directions. Two shotguns start at the center.
  - Phase 3, Murderous Megamoth: up to 7 minions. Sentinels evolve into Micro Megamoth Guardians (Slowed). Pattern A: lunges, 4-way shotguns of green crescents with high armor-piercing damage, pink glaives. Pattern B: slow chase, aimed shotguns of returning green bolts (Quiet) and streams of yellow spinners that stop and become stationary hazards. Special: flashes red, circles the room, leaves leaf projectiles (220 damage) that last 10 seconds.
  - Swarm Tree (treasure room): lobs green bombs in groups of 3, short radial bursts, and rings of stars that start green and harmless, then turn pink (200 damage, Bleeding). It spawns Micro Megamoth Sentinels on death. Clear its guard enemies first.

## Enemies
| Name | Role (regular / miniboss / boss) | Key attacks or behavior | Notes |
|---|---|---|---|
| Forest Goblin Bruiser | regular | Not described | Stronger Forest Maze version |
| Forest Goblin Necromancer | regular | Not described | |
| Grizzled Armored Squirrel | regular | Not described | |
| Mecha Squirrel | regular | Not described | |
| Micro Megamoth Sentinel | regular / boss minion | Confused shots (guide: Unstable) | Evolves into Guardian in phase 3 |
| Micro Megamoth Guardian | regular / boss minion | Slowed shots | |
| Mini Larva | boss minion | Evolves into Sentinel on death | Up to 4 in phase 1 |
| Woodland Paralyze Turret | turret (invincible) | Paralyzed | |
| Woodland Silence Turret | turret (invincible) | Silenced | |
| Woodland Weakness Turret | turret (invincible) | Weak | |
| Woodland Skysplitter Stone | destructible object | Rare drop (pet skin) | |
| Puke Water, Woodland Water | hazard | Sick (Puke Water) | |
| Megamoth Larva / Mammoth Megamoth / Murderous Megamoth | boss (3 phases) | See above | Named "Murderous Megamoth" in the drop tables |
| Swarm Tree | treasure room boss | See above | |
| Possessed Pumpkin, Great Owl, Man-Eating Flytrap, Bloodroot Treant, Hornet's Nest, Legion Head Researcher | outside portal droppers | Possessed Pumpkin: many shots, small pumpkins come alive. Great Owl: circling, fleeing, stationary phases | |

## Tiles and objects to find as sprites
- Floor tiles: Grass, exposed dirt, Puke Water, Woodland Water.
- Wall tiles: Dense trees (the walls), covered tree corridors.
- Hazards and props: Woodland turrets (Paralyze, Silence, Weakness), Puke Water tiles, yellow spinners, leaf projectiles, Skysplitter Stone.
- Other objects (chests, portals, doors, keys): Woodland Labyrinth portal and key. Swarm Tree room. Boss loot bags.

## Loot
- Guaranteed for two players: Greater Potion of Attack and Greater Potion of Vitality. Potions of Mana and Life also drop.
- Untiered: Leaf Bow (+5 Speed, no pierce), Wakizashi of Eastern Winds (Exposed 4.5 s), Labyrinth Dweller's Sheath, Elder Heartwood Staff.
- Woodland Huntress Skin (rarest, soulbound). Blessed Blade Pet Skin (rare, from a destructible object).
- Completion gives Explosive Journey, Epic Battles, Hero of the Nexus and Realm of the Mad God fame bonuses. The page shows "37-44" and "41-47" under Dust Drops, with labels lost.

## Sprite search hints
- Words to search in `Objects.xml` and `GroundTypes.xml`: Woodland, Labyrinth, Megamoth, Larva, Mini Larva, Micro Megamoth, Sentinel, Guardian, Swarm Tree, Turret, Paralyze Turret, Silence Turret, Weakness Turret, Skysplitter, Puke, Forest Goblin, Squirrel, Mecha Squirrel, Treant, Tree.

## Gaps
- Room sizes and counts.
- HP and defense values.
- Exact attack numbers for most enemies. Behavior of goblins and squirrels.
- Sentinel status: main page says Confused, guide says Unstable.
- Exact name of the boss object in the game data.
- Item names in the drop tables were images and are lost.
- Pathway width and tree wall object names.
