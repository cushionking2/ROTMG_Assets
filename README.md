# ROTMG_Assets: RotMG Exalt asset library

Personal, offline use only. Do not share the extracted assets.

## What is here

| Folder | Content |
|---|---|
| `assets\` | About 47,400 sprites from the installed game, sorted by category. `index.json` lists them all. |
| `views\` | One folder per dungeon (26). Enemies, helpers, tiles, walls, props, projectiles, NPCs, loot. `view.json` says why each sprite is there. |
| `docs\` | `EXTRACTION_PLAN.md` (main reference), `RESEARCH_NOTES.md`, and `dungeon_specs\` (26 dungeon specs from saved guides). |
| `tools\` | Python scripts that build everything. |
| `collector\` | Map and behavior recorder. It reads game packets (RealmShark). `captures\` holds the raw recordings. |
| `maps\` | `live\` real dungeon maps from captures. `generated\` maps from our generator. `png\` pictures. |
| `rooms\` | Rooms and room graphs for Pirate Cave, and the measured generator parameters. |
| `behaviors\` | Enemy behavior summaries from captures. |
| `research\` | `X-com_RealmShark`, the packet library. Nothing else. |
| `work\` | Copy of the game, raw exports, and scratch files. About 1.5 GB. Not in git. See "Restore ignored files". |

## Dungeon maps (new)

Layouts come from live packet capture, not from the game files. Read `docs\DUNGEON_PIPELINE.md` for the full process.
The Pirate Cave generator works: `python -I tools\pc_gen.py gen 5`. Findings: `docs\pirate_cave_findings.md`.

## Start here

1. Read `docs\EXTRACTION_PLAN.md`. Section 1 is the status. Section 4 has the rebuild commands.
2. To see sprites for a dungeon, open `views\<Dungeon>\`.
3. To find a sprite by name, search `assets\index.json` (fields: `id`, `category`, `sub`, `src`, `files`, `stats`).
4. Gaps and unresolved names: `views\UNMATCHED.md` and `EXTRACTION_PLAN.md` sections 6 to 8.

## Restore ignored files (new machine)

Git does not hold these paths (see `.gitignore`). Make them again after you clone the repo.
Run all commands from the repo root. The scripts need Python 3 and the packages `UnityPy` and `Pillow` (`pip install UnityPy Pillow==10.4.0`).

| Ignored path | How to get it back |
|---|---|
| `work\game_copy\` | Install RotMG Exalt. Copy the `Production` folder (default: `C:\Users\<you>\AppData\Local\RealmOfTheMadGod\Production`; older installs used `Documents\RealmOfTheMadGod\Production`) to `work\game_copy\`. Use the same game build as the data in `assets\` (7.2.0.1.0). |
| `work\raw_export\` | `python -I tools\export_raw.py "work\game_copy\RotMG Exalt_Data" work\raw_export` |
| `work\objects.json` | This file is in git. To rebuild it: `python -I tools\parse_objects.py work\raw_export\text work\objects.json` |
| `work\jdk\`, `work\jdk_dl\` | Download JDK 17 (Temurin 17, Windows x64 zip) from https://adoptium.net/temurin/releases/?version=17. Unzip it so that `work\jdk\jdk-17.x.y\bin\java.exe` exists. `build.bat` and `run.bat` find the `jdk-*` folder by pattern. |
| `research\X-com_RealmShark\` | `git clone https://github.com/X-com/RealmShark research\X-com_RealmShark` |
| `collector\build\` | Do the JDK and RealmShark steps first. Then run `collector\build.bat`. It writes `collector\build\MapCollector.jar`. |
| `collector\captures\` | Raw packet recordings. They are not in git, because they can hold account or session data. Record new ones with `collector\run.bat` (read `collector\README.md`), or copy the folder from the old machine. The results in `maps\` and `behaviors\` are in git. |
| `work\scratch\`, `work\il2cpp_dump\` | Old one-off scripts and an empty folder. Nothing to restore. |

To make `assets\` and `views\` again from the game files, see "Rebuild from scratch" in `docs\EXTRACTION_PLAN.md` section 4.
Packet capture also needs Npcap (https://npcap.com/#download). Install it with the default options.

## Not done

Game code (the metadata is obfuscated), generators for dungeons other than Pirate Cave, and audio, UI, and particle assets.
