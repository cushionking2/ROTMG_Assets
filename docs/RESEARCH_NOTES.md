# RotMG / Exalt research notes

> **Correction note (2026-11-21).** We have since read the real game data. See `EXTRACTION_PLAN.md` section 3 for verified facts. Where this file disagrees with the plan, the plan is right.
> - Confirmed: `<Texture>` and `<AnimatedTexture>` with `<File>` and `<Index>`. Sheet names such as `lofiObj5`, `lofiChar8x8`, `players`, `playerskins`. Class values Player, Character, Equipment, Projectile, Wall, Container, Portal, GameObject, Skin, Pet (and more: PetSkin, Dye, Title, Emote, Gravestone).
> - Wrong or incomplete: Exalt does not use 8x8 and 16x16 cell grids that you index by position. Sprites sit in three packed atlases (`mapObjects`, `characters`, `groundTiles`). A binary file, `spritesheetf`, maps sheet name and index to a rectangle.
> - Unverified: the SlotType numbers below. The sorter does not use them. It uses `<Labels>` such as `WEAPON,SWORD`.
> - Answered: Unity version is 2022.3.10f1. The atlas format and the XML are inside `resources.assets`. The metadata file is obfuscated.
> - Still open: any DECA policy on asset use.

Status: web search gave thin results. Many facts are NOT confirmed.
Each fact has a tag. [SRC] means a source in the list supports it. [MEM] means it comes from general memory and has no source here. Verify [MEM] items against the real data.
Blocked by tool policy: realmeye.com, google.com, fandom.com were not fetched. The DECA XML guide on sites.google.com was also refused by the tool, so it was not read in full.

## 1. Sprite storage

- Flash-era client: sprites sit in sheets embedded in the SWF. Example sheet name: `lofiChar8x8`. [SRC: S1, via search snippet]
- Objects.xml links an object to a sprite with `<Texture><File>name</File><Index>0xcd</Index></Texture>`. File is the sheet name. Index is a hex cell number. [SRC: S1, via search snippet]
- Animated sprites need `<AnimatedTexture>` instead of `<Texture>`. Otherwise the client errors. [SRC: S1, via search snippet]
- Sheet names such as `characters`, `chars8x8`, `chars16x16`, `chars8x8rBeach` and mask sheets. [MEM, unconfirmed]
- Cell sizes 8x8 and 16x16 pixels. Index counts cells left to right, then top to bottom. [MEM, unconfirmed]
- Mask sheets hold the colour-region data for dyeable clothing. [MEM, unconfirmed]
- GroundTypes.xml holds tile (ground) definitions with a texture and flags such as speed or damage. [MEM, unconfirmed]

## 2. Objects.xml structure

- Each object has an `<Object type="0x..." id="Name">` element. [MEM]
- Class values seen in Flash data: Player, Character, Equipment, Projectile, Wall, Container, Portal, GameObject, Skin, Pet, Merchant. [MEM, unconfirmed]
- Tags: `Projectile` defines a shot. `Tier` gives item tier. These two are confirmed. [SRC: S2, via search snippet]
- Projectile detail (ObjectId, Speed, Damage, LifetimeMS, Amplitude, Frequency, flags like MultiHit, PassesCover, ArmorPiercing). [MEM, unconfirmed]
- Enemy tags: Enemy, MaxHitPoints, Defense, Quest, God, Oryx, Static, Flying. [MEM, unconfirmed]
- Skin entries: Class `Skin`, with `PlayerClassType` pointing to the class. [MEM, unconfirmed]
- RemoteTexture: tag that loads art from a remote URL or instance. [MEM, unconfirmed]
- SlotType numbers (very likely, but unconfirmed): 1 sword, 2 dagger, 3 bow, 4 tome, 5 shield, 6 leather armor, 7 heavy armor, 8 wand, 9 ring, 10 consumable/spell, 11 spell, 12 seal, 13 cloak, 14 robe, 15 quiver, 16 helm, 17 staff, 18 poison, 19 skull, 20 trap, 21 orb, 22 prism, 23 scepter, 24 shuriken, 25 pet food. [MEM, unconfirmed. Do not trust without a check.]
- Equipment has four slot groups: weapon, ability, armor, ring. [SRC: S3, via search snippet]
- Public XML docs exist at DECA's documentation site. [SRC: S1]

## 3. Exalt specifics

- Exalt is the Unity port of RotMG. Release date 22 July 2020. [SRC: S4, via search snippet]
- Unity 2022.3 comes from the task brief. Not confirmed by any source found.
- Muledump asset compiler reads `RotMG Exalt_Data/resources.assets`. [SRC: S5]
- That tool runs AssetRipper on `resources.assets`. [SRC: S5]
- Then a modified "Haizor ROTMG Asset Ripper" runs. It "converts new sprite atlases into the old style spritesheets". [SRC: S5]
- Output files of that chain: `constants.js`, `renders.png`, `sheets.js`. [SRC: S5]
- The Exalt atlas format (sprite names, rects) is not documented in the sources found.
- The rotmg-network GitHub org lists: `exalt-extractor` (Python, no description), `Exalt-Metadata-Dumper` (C, fork), `Il2CppInspectorFix`, `ExaltDumper` (C#). [SRC: S6]
- Exalt-Metadata-Dumper is described as a tool that decrypts the global metadata header, reverses a shuffle, and builds a usable `global-metadata.dat`. [SRC: S6]
- Meaning: Exalt probably protects `global-metadata.dat`. Il2CppDumper may fail on the raw file. [Inference from S6, unconfirmed]
- Sprite and texture export does not need IL2CPP metadata. AssetStudio and AssetRipper read `resources.assets` and `.bundle` files directly. [S5 supports AssetRipper use; the rest is MEM]
- Generic AssetStudio flow for IL2CPP games: run Il2CppDumper, then give AssetStudio the dummy DLL folder. Only needed to read MonoBehaviour data. [SRC: S7, via search snippet]
- AssetStudio note: sprites are cropped regions of a parent texture. Find the texture to recover the sprite. [SRC: S7, via search snippet]
- Cpp2IL and UnityPy use on Exalt: no source found.

## 4. Game design basics (all [MEM], unconfirmed)

- Classes: Rogue, Archer, Wizard, Priest, Warrior, Knight, Paladin, Assassin, Necromancer, Huntress, Mystic, Trickster, Sorcerer, Ninja, Samurai, Bard, Summoner, Kensei.
- Item slots: weapon, ability, armor, ring.
- Tiers: T0 to T15 for weapons and armor. Abilities go to T6. Rings go to T6. UT (untiered), ST (set tier) and white-bag items exist.
- Loot bag colours: brown, pink, purple, cyan, blue, white (rising rarity).
- Enemy families: Pirate Cave, Snake Pit, Spider Den, Sprite World, Cube and Oryx minions, Gods (Medusa, Beholder, Flying Brain), Tomb guardians, and so on.
- Realm structure: the Realm hub, then dungeons. Dungeon types: low-level (Pirate Cave, Forest Maze), mid (Snake Pit, Abyss, Tomb), end-game (Shatters, Nest, Void, Cultist Hideout, Oryx Sanctuary), event dungeons.
- Other asset groups worth sorting: pets, UI icons, particles, status-effect icons, portals, walls, floor tiles, containers (bags), NPCs.

## 5. Legal / terms of use

- RotMG is owned and run by DECA Games. [SRC: S8, via search snippet]
- No DECA fan-content or asset-extraction policy was found. Facts about permission: unknown.
- The `Exalt-Metadata-Dumper` tool exists to defeat the metadata protection. A search summary said such tools could help build bots or cheats, which violate game terms. This is a model summary, not a quote of the terms.
- Read the DECA Terms of Service directly before use.

## Sources

- S1: https://sites.google.com/decagames.com/xml-documentation/xml-guide (snippet via search only)
- S2: https://www.realmeye.com/compare-revisions-of-wiki-page/how-to-find-object-data/1 (search snippet only, not fetched)
- S3: https://www.realmeye.com/wiki/rings/156 (search snippet, equipment slots)
- S4: https://realmeye.com/wiki/realm-of-the-mad-god-exalt (search snippet)
- S5: https://github.com/jakcodex/muledump-asset-compiler
- S6: https://www.github.com/rotmg-network
- S7: https://github.com/AtlyssModding/ATLYSS-Modding-Resources/wiki/How-to-preview-&-export-game-assets (generic AssetStudio flow)
- S8: https://www.wikipedia.org/wiki/Wild_Shadow_Studios (search snippet)
- Tools named, not read: https://github.com/Perfare/UnityStudio, https://github.com/aelurum/AssetStudio, https://github.com/LukeFZ/Il2CppInspectorRedux

## Uncertain / not found

- Exact sheet names and cell layout in Exalt. Not found.
- Exalt atlas format. Not found.
- Unity version 2022.3. Not confirmed by a source.
- Full SlotType table. Only [MEM] values above.
- Full Class list in Objects.xml. Only [MEM] values above.
- GroundTypes.xml fields. Not found.
- RemoteTexture semantics. Not found.
- Whether Exalt still ships Objects.xml, or stores data in another form (for example bundles or ScriptableObjects). Not found.
- Use of Cpp2IL or UnityPy on Exalt. Not found.
- DECA terms on extracted assets. Not found.
- Class list, tiers, enemy and dungeon lists. Not sourced.
- Next step: inspect the installed game files. Check the real data first, then treat this file as hints only.
