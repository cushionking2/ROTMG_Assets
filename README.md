# D_Sim: RotMG Exalt asset library

Personal, offline use only. Do not share the extracted assets.

## What is here

| Folder | Content |
|---|---|
| `assets\` | About 34,300 sprites from the installed game, sorted by category. `index.json` lists them all. |
| `views\` | One folder per dungeon (26). Enemies, helpers, tiles, walls, props, projectiles, NPCs, loot. `view.json` says why each sprite is there. |
| `docs\` | `EXTRACTION_PLAN.md` (main reference), `RESEARCH_NOTES.md`, and `dungeon_specs\` (26 dungeon specs from saved guides). |
| `tools\` | Python scripts that build everything. |
| `collector\` | Map and behavior recorder. It reads game packets (RealmShark). `captures\` holds the raw recordings. |
| `maps\` | `live\` real dungeon maps from captures. `generated\` maps from our generator. `png\` pictures. |
| `rooms\` | Rooms and room graphs for Pirate Cave, and the measured generator parameters. |
| `behaviors\` | Enemy behavior summaries from captures. |
| `research\` | `X-com_RealmShark`, the packet library. Nothing else. |
| `work\` | Copy of the game, raw exports, and scratch files. About 1.1 GB. Safe to rebuild. |

## Dungeon maps (new)

Layouts come from live packet capture, not from the game files. Read `docs\DUNGEON_PIPELINE.md` for the full process.
The Pirate Cave generator works: `python -I tools\pc_gen.py gen 5`. Findings: `docs\pirate_cave_findings.md`.

## Start here

1. Read `docs\EXTRACTION_PLAN.md`. Section 1 is the status. Section 4 has the rebuild commands.
2. To see sprites for a dungeon, open `views\<Dungeon>\`.
3. To find a sprite by name, search `assets\index.json` (fields: `id`, `category`, `sub`, `src`, `files`, `stats`).
4. Gaps and unresolved names: `views\UNMATCHED.md` and `EXTRACTION_PLAN.md` sections 6 to 8.

## Not done

Game code (the metadata is obfuscated), generators for dungeons other than Pirate Cave, and audio, UI, and particle assets.
