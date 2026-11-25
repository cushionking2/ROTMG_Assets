# Map collector

Records the map tiles and objects that the game server sends to the client.
It uses the RealmShark library (`research/X-com_RealmShark`). It only listens. It cannot send, block or change packets.

## Setup (one time)
1. Install Npcap from https://npcap.com/#download (Windows). Use the default options.
2. The JDK, libraries and build are already in this folder (`work/jdk`, `collector/lib`, `collector/build`).
   Run `build.bat` again only if you change `src/MapCollector.java`.

## Use
1. Run `run.bat` BEFORE you enter a dungeon. Start the game after the collector, or at least enter a new world after it starts.
2. Walk the whole dungeon. The server sends only the tiles near you.
3. Leave the dungeon. The collector writes one `captures/<time>_<map>.jsonl` file per map.
4. Run `python -I tools/capture_to_map.py` from the D_Sim folder. It writes `maps/live/*.json`.
5. Run `python -I tools/jm_render.py` to make PNG previews of the live maps in `maps/png/`.

## Behaviour events (new)
Each map also gets `captures/<time>_<map>.events.jsonl`. It holds:
tick (positions and stat changes of all objects), upd (new objects with HP, loot, portal names, and dropped ids),
eshoot (enemy bullets), dmg, aoe, fx, text, notif, goto, quest, self (your object id), pshoot (your shots).
Run `python -I tools/analyze_events.py` from the D_Sim folder. It writes `behaviors/<capture>.md` and `.json`:
per enemy type max HP, speed, shot patterns, shot interval, HP range of each shot type, speech, loot bags.
Events files are large. Expect a few MB per dungeon run.

## Check it works
The `[status]` line prints every 10 seconds. `packetTypes` must be above 0 while the game runs.
If it stays 0, the sniffer sees no game traffic. Check Npcap, and run the collector before the game.
If `tiles` stays 0 but packets arrive, the packet format changed. The `raw` field keeps the bytes for re-decoding.

## Status
Map capture: tested live (7 maps). Behaviour events: compiled and tested offline with synthetic packets only. NOT yet tested live.
