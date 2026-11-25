# Dungeon Spec Index

26 specs. Source: saved Realmeye pages in `C:\Users\Austin\Downloads\rotmg dungeons\`.
Format: see `_TEMPLATE.md`. Every spec has a "Gaps" section.

| Spec | Boss (from spec) | Layout type | Notes |
|---|---|---|---|
| Abyss_of_Demons | Archdemon Malphas | Lava room network | Boss room 10 rooms from spawn |
| Candyland_Hunting_Grounds | Cupcake (after 5 boss types) | Round rooms | |
| Cave_of_a_Thousand_Treasures | Golden Oryx Effigy | Fixed 8-room line | Wiki and guide disagree on trap room number |
| Crawling_Depths | Son of Arachna | Chain of cave rooms | 4 colored eggs |
| Cursed_Library | Avalon, Corruption Phantom (secret) | Branching maze | Pressure plates |
| Davy_Jones_Locker | Davy Jones | Key and door rooms | 4 keys |
| Deadwater_Docks | Jon Bilgewater | Island map | 5 boss phases |
| Forbidden_Jungle | Mixcoatl | Rooms and hallways, or mostly linear | Main page and guide. Pages disagree on layout and portal drops |
| Forest_Maze | Mama Megamoth | Procedural rooms | |
| Haunted_Cemetery | Skuld | 3 fixed arenas | Waves |
| Hive | Queen Bee | Bee rooms | Honey slows |
| Lost_Halls | Several | 8x8 to 9x9 room grid | Large spec |
| Mad_Lab | Two bosses | Lab rooms | Tesla Coils, Lab Vats |
| Magic_Woods | Fountain Spirit | Small forest | Guide page only |
| Manor_of_the_Immortals | Lord Ruthven | 9 rooms to boss | Hidden treasure rooms |
| Ocean_Trench | Thessal | Underwater | Guide page only, 2021 |
| Oryxs_Castle | Stone Guardians, Janus (secret) | Static 4-wing castle | |
| Parasite_Chambers | Nightmare Colony | Infested rooms | Explosive barrels |
| Pirate_Cave | Dreadstump | Ship and islands | No walls |
| Puppet_Masters_Theatre | Puppet Master | Procedural room maze | |
| Snake_Pit | Stheno | 5 circular rooms | Breakable blocks |
| Spider_Den | Arachna | Linear circular rooms | Egg sacs, cobwebs |
| Sprite_World | Limon | Floating platforms | No walls |
| Toxic_Sewers | Gulpord | Sludge corridors | Slime God count disagrees between pages |
| Undead_Lair | Septavius | 9 rooms to boss | Hidden traps |
| Woodland_Labyrinth | Megamoth | Tree-walled rooms | Sentinel status disagrees between pages |

## Cross-check with the game data (2026-11-21)

- Sprites for each dungeon are in `D_Sim\views\<Dungeon>\`. The table of dungeon to game XML source is in `EXTRACTION_PLAN.md` section 6.
- Wiki names that differ from game names: Crawling Depths = `epicspiderDen`, Davy Jones' Locker = `ghostShip`, Hive = `thehive`, Woodland Labyrinth = `epicforestMaze`. Many enemy names differ in display (for example Blood Hound = `Sanguine Hound`).
- Names with no game object: Druid Puppet (no Druid class in this build), Ghost Slurp, Legion Lead Strategist, Legion Surveyor, Legion Head Researcher. See `views\UNMATCHED.md`.
- The game data has stats (HP, defense, XP, projectiles) but no map layouts. Room sizes and layout logic come only from these specs.
- The Haunted Cemetery wave minions, for example, map to `Arena Mushroom` (Troll's Toadstool), `Arena Pumpkin` (Haunted Pumpkin), `Arena Blue Flame` (Forgotten Spiraling Soul), and `Blue Zombie` (Crawling Zombie).

## Known gaps across all specs
- Item names in drop tables are missing. The wiki shows icons only. Get names from `Objects.xml`.
- Tile names and most room sizes are missing.
- Treat each spec as a lead, not as verified data. Check against `Objects.xml` and the game.
