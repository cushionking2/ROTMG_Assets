# RotMG Exalt Asset Extraction

Purpose: extract and sort sprites and data from the user's installed Realm of the Mad God Exalt, for personal, offline use only.
This file is the main reference. Last full update: 2026-11-25 (full rebuild from the updated install, game build 7.2.0.1.0, on a new machine).

## 1. Status

| Area | State |
|---|---|
| Copy of the install | Done. `work\game_copy\` (66 files, 1.2 GB). The install is untouched. |
| Raw export | Done. 259 text assets (the game's XML), 309 textures, 1,087 UI sprites. 13 textures fail and are skipped: 12 empty 0x0 font textures and 1 unnamed engine texture in `globalgamemanagers.assets`. |
| Sprite library | Done. About 47,400 sprites in `assets\`, with `assets\index.json`. |
| Enemy tiers and helpers | Done. See section 7. |
| Per-dungeon views | Done. 26 dungeons in `views\`. See section 6. |
| Dungeon specs | Done. 26 specs in `docs\dungeon_specs\`. |
| Game code (IL2CPP dump) | **Not done.** The metadata file is obfuscated. We chose to skip it. |
| Dungeon map layouts | **Not in the game data.** Captured live from packets: see `docs/DUNGEON_PIPELINE.md`. |
| Audio, UI, particles, dye masks | Not extracted. |
| `assets\helper\other` (415 objects) | Left as is, by decision. Review later if needed. |

## 2. Install facts

| Item | Value |
|---|---|
| Game folder | `C:\Users\<you>\AppData\Local\RealmOfTheMadGod\Production\` (older installs: `Documents\RealmOfTheMadGod\Production\`) |
| Data folder | `...\Production\RotMG Exalt_Data\` |
| Unity version | 6000.0.58f2 (2022.3.10f1 before the 2026-11-25 rebuild) |
| Backend | IL2CPP (`GameAssembly.dll`, 75 MB) |
| Metadata | `il2cpp_data\Metadata\global-metadata.dat`, 17 MB. **Obfuscated.** First bytes `41 0F F2 FE` (before 2026-11-25: `89 36 15 FF`) (normal: `AF 1B B1 FA`). Il2CppDumper stops with "Metadata file not found or encrypted". |
| Main asset files | `resources.assets` (410 MB), `sharedassets0-4.assets`, `globalgamemanagers.assets`, plus `.resS` and `resources.resource` streams |
| `Desktop\exalt\MultiTool_Data\Objects.xml` and `GroundTypes.xml` | **Not used.** Source not verified. The game holds its own XML (section 3). |
| Python | 3.12 (3.9 also works). Needs `UnityPy` 1.25.4 and `Pillow` 10.4.0 (Pillow 8.3.1 breaks texture decoding). |

## 3. How the game stores its data (verified)

- **Data is XML inside the game.** The TextAssets in `resources.assets` hold `players`, `equip`, `equipSkins`, `skins`, `projectiles`, `containers`, `portals`, `pets`, `ground`, and one `<dungeon>Objects` plus `<dungeon>Ground` pair per dungeon. `manifest.json` lists the files by dungeon. The XML has stats (HP, defense, XP, projectiles), `<Labels>`, `<Group>`, and `<DisplayId>`. It has no behavior and no map layouts.
- **Art is in three atlases** (PNG after export): `mapObjects` (8192x4096), `characters` (8192x4096), `groundTiles` (2048x2048). `characters_masks` holds dye masks (not used).
- **XML to atlas link.** An object has `<Texture>` or `<AnimatedTexture>` with `<File>` (a sheet name such as `lofiObj5`) and `<Index>`. `RandomTexture` can hold several of either.
- **`spritesheetf`** (a TextAsset, 13.3 MB) is a FlatBuffers file with two root vectors. Decoder: `tools\ssf.py`.
  - Vector 1, 288 sheets, static sprites. The record whose field `f3` equals the XML `<Index>` is the sprite (no `f3` means index 0). It holds a rectangle `(x, y, w, h)` in an atlas.
  - Vector 2, 54,755 records, animated character frames. Match `sheet == <File>` and `f1 == <Index>`. Records for one index keep file order. Most have 18 frames: 3 directions of 6. Field `f4` is the frame type (0 stand, 1 walk, 2 attack). Frame order is verified for the Rogue only.
  - Field `f7` picks the atlas: 1 = `groundTiles` (the rectangle has 1 px padding), 2 = `characters`, 4 = `mapObjects`. The y axis is top-down, as in the PNG files saved by UnityPy.
- **Items carry `<Labels>`**, for example `EQUIPMENT,WEAPON,SWORD,TIERED`. The sorter uses them.

## 4. Tools

Used (in `tools\`, run with `python -I` from the repo root):

| Script | Job |
|---|---|
| `survey_assets.py` | Count asset types per file. Output `work\asset_survey.json`. |
| `export_raw.py` | Export TextAssets (`.xml`, `.json`, `.txt`, `.bin`), textures, and UI sprites to `work\raw_export\`. |
| `parse_objects.py` | Read all XML into `work\objects.json` (ids, classes, labels, textures, HP, XP, flags). |
| `ssf.py` | Decode `spritesheetf.bin`. |
| `build_sprites.py` | Crop sprites, sort them, write `assets\` and `assets\index.json`. |
| `build_dungeon_views.py` | Build `views\`, `views\README.md`, `views\UNMATCHED.md`. |
| `match_dungeons.py` | First pass: which game XML belongs to which spec. Output `work\dungeon_match.json`. |
| `contact_sheet.py`, `src_sheet.py` | Make labeled contact sheets for a quick visual check. |

Installed in `C:\Users\Austin\Desktop\UnityDecompilers\` but not needed so far: AssetStudio, AssetRipper, UABEA, Il2CppDumper (blocked), Cpp2IL, dnSpy, Ghidra, Aseprite, MDB (runtime tool, see section 9). UnityPy did all the extraction.

### Rebuild from scratch

```
cd <repo root>
python -I tools\export_raw.py "work\game_copy\RotMG Exalt_Data" work\raw_export
python -I tools\parse_objects.py work\raw_export\text work\objects.json
python -I tools\build_sprites.py .            # about 45 s. Delete assets\ first.
python -I tools\build_dungeon_views.py .      # a few seconds. Rebuilds views\.
```

Both build scripts expect `work\raw_export\text\spritesheetf.bin`. `export_raw.py` now writes it. If the game updates, copy the new `RotMG Exalt_Data` into `work\game_copy\` first.

## 5. Folder layout

```
D_Sim/
  README.md                    short orientation
  docs/
    EXTRACTION_PLAN.md         this file
    RESEARCH_NOTES.md          web research (thin; read its correction note)
    dungeon_specs/             26 specs, INDEX.md, _TEMPLATE.md
  tools/                       scripts (section 4)
  work/                        game_copy, raw_export, il2cpp_dump (empty), objects.json,
                               asset_survey.json, dungeon_match.json, enemy_stats.json (old), scratch/ (old one-off scripts)
  assets/<category>/<sub>/     sorted sprites, and index.json
  views/<Dungeon>/<group>/     per-dungeon copies, view.json, README.md, UNMATCHED.md
```

`assets\<category>\<sub>\<id>__<typehex>.png` is one sprite. Animated objects also have `_frames\<name>.png` (all frames in rows of 6). The main PNG of an animated object is the standing frame of the second direction group.

### Categories (`categorize()` in `build_sprites.py`)

tile, wall, prop, container, portal, gravestone, player, skin, pet, pet_skin, weapon (sword, dagger, bow, staff, wand, katana, other), armor (leather, heavy, robe), ability, ring, consumable, item_other, projectile, enemy, helper, npc, misc. Tiles, walls, and props are grouped by their source XML (that is, by dungeon or realm area).

## 6. Dungeon views

`views\<Dungeon>\` holds copies of the sprites that belong to one dungeon, in groups: `enemies`, `helpers`, `tiles`, `walls`, `props`, `projectiles`, `npcs`, `portals`, `containers`, `loot`. `view.json` stores the reason (`why`) for each sprite:

| why | Meaning | Reliability |
|---|---|---|
| src | Defined in the dungeon's own game XML | High |
| spec | Name in the spec's Enemies table matches an object id, DisplayId, or Group (lists split, prefixes expanded) | High |
| alias | Hand-checked mapping (table below) | Medium to high |
| proj | Fired by an enemy of the view | High |
| loot | Item name found in the spec's Loot section (not after "like", "than", ...) | Medium |
| tile, wall | Spec tile hint matches a global tile or wall (exact name, or only a neutral word added, or a dungeon prefix) | **Low. A guess.** The game data does not say which tile a dungeon uses. |
| spec~ | A single multi-word suggestion, accepted unverified | Low |

### Dungeon to game XML source

| Spec | Game XML source names |
|---|---|
| Abyss of Demons | abyssOfDemons, abyssOfDemonsObjects, abyssOfDemonsGround |
| Candyland Hunting Grounds | candyLand |
| Cave of a Thousand Treasures | caveOfAThousandTreasures |
| Crawling Depths | epicspiderDen |
| Cursed Library | cursedLibraryObjects, cursedLibraryGround |
| Davy Jones' Locker | ghostShip |
| Deadwater Docks | deadwaterDocksObjects, deadwaterDocksGround |
| Forbidden Jungle | forbiddenJungle |
| Forest Maze | forestMaze |
| Haunted Cemetery | hauntedCemetery |
| Hive | thehive |
| Lost Halls | lostHallsObjects, lostHallsGround |
| Mad Lab | madLab |
| Magic Woods | magicWoodsObjects, magicWoodsGround |
| Manor of the Immortals | manorOfTheImmortals |
| Ocean Trench | oceanTrench |
| Oryx's Castle | oryxCastle |
| Parasite Chambers | parasiteDenObjects, parasiteDenGround |
| Pirate Cave | pirateCaveObjects, pirateCaveGround |
| Puppet Master's Theatre | puppetMaster |
| Snake Pit | snakePit |
| Spider Den | spiderDenObjects, spiderDenGround |
| Sprite World | spriteWorldObjects, spriteWorldGround |
| Toxic Sewers | toxicSewersObjects, toxicSewersGround |
| Undead Lair | undeadLair, undeadLairObjects, undeadLairGround |
| Woodland Labyrinth | epicforestMaze |

Several of the wiki names differ from the game names. The `pirateCave`, `spiderDen`, `spriteWorld`, and `toxicsewers` files are empty.

### Name matches done by hand (`ALIASES`)

| Spec name | Game object | Basis |
|---|---|---|
| Troll's Toadstool | `Arena Mushroom` | Sprite and spec text (minion thrown by the Troll Matriarch) |
| Haunted Pumpkin | `Arena Pumpkin` | Sprite and spec text (circles the Pumpkin King) |
| Forgotten Spiraling Soul | `Arena Blue Flame` | Sprite and spec text (thrown by the Grave Caretaker) |
| Crawling Zombie | `Blue Zombie`, `Zombie Rise` | Sprite and spec text (swarms) |
| Burning Bones | `Flaming Skeleton` (file `adept`, Risen Hell) | Sprite |
| Trickster Puppet Decoy | `Trickster Decoys` | Name |
| Sludge | `DS Sludge Tile` and variants | It is a floor hazard |
| Treasure Mimic | `Treasure Enemy` | **Probable only.** Chest-with-eyes sprite that shoots coins |
| Lab Vat | `Lab Good Vat`, `Lab Bad Vat` tiles | Name |
| Honey | `TH Honey` tile | Name |

### Still unresolved (also in `views\UNMATCHED.md`)

- Druid Puppet. This build has no Druid class in `players.xml`. The wiki pages may be newer than the install.
- Ghost Slurp. The only Slurp in the Parasite Chambers file is `pD Blood Slurp`.
- Legion Lead Strategist, Legion Surveyor, Legion Head Researcher. The data has only Legion General, Footsoldier, Major, Spear, and beacon guardians.
- "Parasite Chambers monsters" is a note, not an object.

## 7. Enemy tiers and helpers

The `BOSS`, `BOSS_SPAWNED`, and `HealthBarBoss` tags also sit on loot markers, anchors, clones, and effects. So the sorter uses HP and flags too:

- No HP, or `Invincible`, or a Moonlight Village loot or XP marker: category `helper`. Subfolders by name (whole words): `invisible` (texture `invisible`), `loot_marker`, `spawner`, `effect`, `anchor`, `other`.
- Otherwise `enemy`: `boss` (label BOSS), `miniboss` (label MINIBOSS), `boss_minion` (label BOSS_SPAWNED), `event_boss` (HealthBarBoss or Quest, no BOSS or MINIBOSS label: realm events), `regular`.

Counts: boss 79, miniboss 135, event_boss 209, boss_minion 50, regular 2,429; helper 1,000 (other 415, invisible 286, anchor 106, effect 96, spawner 61, loot_marker 43).

Known odd entries in `boss`: `TestChicken 2`, `KSW Factory Control Core`, `SW Gift Boss`, `mc`. `helper\other` holds boss parts with no HP (for example Boss Totem), turrets, and some NPCs.

## 8. Known limits

- Only the first sprite variant is saved for objects with random sprites (`variants` in `index.json` gives the count).
- 221 objects have no texture in the XML (invisible helpers, remote textures). They are not in the index.
- Tile edge and blend variants in `groundTiles` that no XML object uses are not extracted.
- Frame order for animated sprites is checked on the Rogue only.
- Loot and tile matching in the views is name based. Treat it as a lead.
- The specs came from saved wiki pages. Some may describe a newer game version than the install.

## 9. Possible next steps

1. Review `helper\other` when something is missing.
2. Export other asset types: audio (239 clips in `resources.assets`), UI atlas, particles, dye masks.
3. Game code. The metadata is obfuscated.
   - Static route: use Ghidra on `GameAssembly.dll` to find the metadata loader and its decryption, then decrypt offline and run Il2CppDumper.
   - Runtime route: the MDB framework in `UnityDecompilers\MDB` loads inside the running game. That reads process memory of an online game and may risk the account. Do not do it unless the user asks.
4. Build the game from the library and the specs. Map layouts and room sizes must come from the specs and the guides.

## 10. Rules

- Personal, offline use only. Do not share or publish extracted assets.
- Do not scrape Realmeye, Google, or Fandom. Use the saved pages.
- Do not read process memory. Do not decrypt the metadata unless the user asks.
- The repo is in git, but the ignored paths (see `.gitignore`) are not. Deletions there are permanent. Ask before deleting.
- Write all text in Simplified Technical English.

## 11. Lessons

- The game XML inside the game replaces any third-party `Objects.xml`.
- Labels are not enough to sort enemies. Use HP and flags.
- Wiki names often differ from game ids and display names. Search ids, `DisplayId`, and `Group`, and read the dungeon's own file.
- In a Python heredoc, regex backslashes can turn into control characters (`\b` becomes a backspace). Write patterns in a file with a raw string, or use the Edit tool.
