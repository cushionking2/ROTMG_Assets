"""Build per-dungeon sprite views from assets/index.json, game XML sources, and docs/dungeon_specs/*.md.

Usage: python -I build_dungeon_views.py <D_Sim root>
Output: views/<Dungeon>/<group>/<sub>/*.png, views/<Dungeon>/view.json, views/README.md, views/UNMATCHED.md
A sprite joins a view for one of these reasons (stored as "why"):
  src   : the object is defined in one of the dungeon's own game XML files (SRCS below)
  spec  : the object id, DisplayId, or Group equals a name in the spec's Enemies table (lists are split, shared
          prefixes are expanded: "Lair Ghost Archer, Knight" -> "Lair Ghost Knight")
  proj  : an enemy of the view fires this projectile (Projectile/ObjectId)
  loot  : an item name appears in the spec's "## Loot" section (>= 8 chars, whole words, not in a comparison)
  tile  : a global ground tile (ground.xml) whose name matches a tile hint in the spec
  alias : a hand-checked mapping from a spec name to a game id (ALIASES)
  wall  : a global wall (objects.xml / staticobjects.xml) whose name matches a hint in the spec
Names that match nothing are written to views/UNMATCHED.md, with unverified suggestions.
"""
import sys, os, re, json, shutil, collections, difflib
root = sys.argv[1]
W = lambda *p: os.path.join(root, *p)

SRCS = {  # spec name -> game XML source names (TextAsset names). Found with tools/match_dungeons.py.
    'Abyss_of_Demons': ['abyssOfDemons', 'abyssOfDemonsObjects', 'abyssOfDemonsGround'],
    'Candyland_Hunting_Grounds': ['candyLand'],
    'Cave_of_a_Thousand_Treasures': ['caveOfAThousandTreasures'],
    'Crawling_Depths': ['epicspiderDen'],
    'Cursed_Library': ['cursedLibraryObjects', 'cursedLibraryGround'],
    'Davy_Jones_Locker': ['ghostShip'],
    'Deadwater_Docks': ['deadwaterDocksObjects', 'deadwaterDocksGround'],
    'Forbidden_Jungle': ['forbiddenJungle'],
    'Forest_Maze': ['forestMaze'],
    'Haunted_Cemetery': ['hauntedCemetery'],
    'Hive': ['thehive'],
    'Lost_Halls': ['lostHallsObjects', 'lostHallsGround'],
    'Mad_Lab': ['madLab'],
    'Magic_Woods': ['magicWoodsObjects', 'magicWoodsGround'],
    'Manor_of_the_Immortals': ['manorOfTheImmortals'],
    'Ocean_Trench': ['oceanTrench'],
    'Oryxs_Castle': ['oryxCastle'],
    'Parasite_Chambers': ['parasiteDenObjects', 'parasiteDenGround'],
    'Pirate_Cave': ['pirateCaveObjects', 'pirateCaveGround'],
    'Puppet_Masters_Theatre': ['puppetMaster'],
    'Snake_Pit': ['snakePit'],
    'Spider_Den': ['spiderDenObjects', 'spiderDenGround'],
    'Sprite_World': ['spriteWorldObjects', 'spriteWorldGround'],
    'Toxic_Sewers': ['toxicSewersObjects', 'toxicSewersGround'],
    'Undead_Lair': ['undeadLair', 'undeadLairObjects', 'undeadLairGround'],
    'Woodland_Labyrinth': ['epicforestMaze'],
}
PREFIX = {'Hive': {'th'}, 'Toxic_Sewers': {'ds'}, 'Mad_Lab': {'lab'}, 'Parasite_Chambers': {'pd'}, 'Magic_Woods': {'mw'}}  # object-name prefixes the game uses
# spec name -> regex on game object ids (found by hand from the suggestions in UNMATCHED.md)
ALIASES = {
    'Mad_Lab': {'Lab Vat': r'^Lab (Good|Bad) Vat'},
    'Hive': {'Honey': r'^TH Honey$'},
    # checked by eye against the sprite sheets and the spec text (see docs/EXTRACTION_PLAN.md)
    'Cave_of_a_Thousand_Treasures': {'Treasure Mimic': r'^Treasure Enemy$'},  # probable: chest creature that shoots coins
    'Haunted_Cemetery': {"Troll's Toadstool": r'^Arena Mushroom$', 'Haunted Pumpkin': r'^Arena Pumpkin$',
                         'Forgotten Spiraling Soul': r'^Arena Blue Flame$', 'Crawling Zombie': r'^(Blue Zombie|Zombie Rise)$'},
    'Puppet_Masters_Theatre': {'Trickster Puppet Decoy': r'^Trickster Decoys$'},
    'Toxic_Sewers': {'Sludge': r'^DS Sludge Tile'},
    'Undead_Lair': {'Burning Bones': r'^Flaming Skeleton$'},  # Risen Hell realm enemy, file adept
}
GLOBAL_TILE_SRCS = {'ground'}
GLOBAL_WALL_SRCS = {'objects', 'staticobjects'}
SPEC_CATS = {'enemy', 'helper', 'npc', 'prop', 'container', 'portal', 'wall', 'tile'}  # classes a spec name may resolve to

n = lambda s: re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()
def sing(s): return ' '.join(w[:-1] if len(w) > 3 and w.endswith('s') and not w.endswith('ss') else w for w in s.split())
def toks(s): return {re.sub(r'\d+$', '', w) or w for w in sing(n(s)).split()}

idx = json.load(open(W('assets/index.json')))
objs = json.load(open(W('work/objects.json')))
disp = {(o['src'], o['id'], o['type']): o['display'] for o in objs}
projs = {(o['src'], o['id'], o['type']): [p[1] for p in o['proj'] if p[1]] for o in objs}
by_name = collections.defaultdict(list)
for r in idx:
    for nm in (r['id'], disp.get((r['src'], r['id'], r['type']))):
        if nm:
            by_name[n(nm)].append(r)
            if sing(n(nm)) != n(nm): by_name[sing(n(nm))].append(r)
grp = {(o['src'], o['id'], o['type']): o['group'] for o in objs}
by_group = collections.defaultdict(list)
for r in idx:
    g = grp.get((r['src'], r['id'], r['type']))
    if g: by_group[n(g)].append(r)
all_names = list(by_name)
proj_by_id = collections.defaultdict(list)
for r in idx:
    if r['category'] == 'projectile': proj_by_id[r['id']].append(r)
loot_cats = {'weapon', 'armor', 'ability', 'ring', 'consumable', 'item_other'}
loot_recs = [r for r in idx if r['category'] in loot_cats and len(n(r['id'])) >= 8]
global_tiles = [r for r in idx if r['category'] == 'tile' and r['src'] in GLOBAL_TILE_SRCS]
global_walls = [r for r in idx if r['category'] == 'wall' and r['src'] in GLOBAL_WALL_SRCS]

def section(text, title):
    m = re.search(r'## ' + re.escape(title) + r'[^\n]*\n(.*?)(?=\n## |\Z)', text, re.S)
    return m.group(1) if m else ''

def spec_names(spec):
    """Names from the Enemies table. Splits lists and slash groups, and expands shared prefixes."""
    out = []
    for line in section(spec, 'Enemies').splitlines():
        if not line.startswith('|') or line.startswith('|---') or line.lower().startswith('| name'): continue
        raw = re.sub(r'\(.*?\)', '', line.split('|')[1]).strip()
        parts = [p.strip() for p in re.split(r',| / | and ', raw) if p.strip()]
        first_words = parts[0].split() if parts else []
        for i, part in enumerate(parts):
            if '/' in part:
                m = re.match(r'^(.*?)(\w+(?:/\w+)+)\s+(.*)$', part)
                if m:
                    out += [(m.group(1) + a + ' ' + m.group(3)).strip() for a in m.group(2).split('/')]
                    continue
            cand = [part]
            if i > 0 and len(part.split()) == 1 and len(first_words) > 1:
                cand.insert(0, ' '.join(first_words[:-1] + [part]))  # shared prefix: "Lair Ghost Archer, Knight"
            out.append(cand)
    return [c if isinstance(c, list) else [c] for c in out]

def hints(spec):
    """Tile/wall hint phrases: the GroundTypes hint list plus short pieces of the Floor/Wall tile lines."""
    ph = set()
    for line in spec.splitlines():
        low = line.lower()
        if 'groundtypes.xml' in low and ':' in line:
            tail = line.split('`:', 1)[-1] if '`:' in line else line.split(':', 1)[-1]
            for p in re.split(r',|;|\.', tail): ph.add(n(p))
        elif low.startswith('- floor tiles:') or low.startswith('- wall tiles:'):
            for p in re.split(r',|;|\.| and ', line.split(':', 1)[1]):
                p = n(p)
                if 0 < len(p.split()) <= 3: ph.add(p)
    return {p for p in ph if len(p) >= 3}

NEUTRAL = {'light', 'dark', 'bright', 'deep', 'shallow', 'new'}  # themed variants (Candy Grass, Zombie Dirt) are not matched
def hint_match(name, ph, extra=frozenset()):
    nt = toks(name)
    for h in ph:
        ht = toks(h)
        if ht and ht <= nt and (nt - ht) <= (NEUTRAL | extra): return h  # exact name, or only neutral modifiers added
    return None

def loot_hit(text_loot, name):
    nn = n(name)
    for m in re.finditer(r'(?<![a-z0-9])' + re.escape(nn).replace(r'\ ', r'\s+') + r'(?![a-z0-9])', n(text_loot)):
        before = n(text_loot)[max(0, m.start() - 30):m.start()]
        if re.search(r'\b(like|similar to|unlike|than|versus|beat|beaten by|over|instead of)\b', before): continue
        return True
    return False

def group_of(r):
    c, s = r['category'], r['sub']
    if c == 'enemy': return 'enemies', s
    if c == 'helper': return 'helpers', s
    if c in ('tile', 'wall', 'prop'): return {'tile': 'tiles', 'wall': 'walls', 'prop': 'props'}[c], 'all'
    if c in loot_cats: return 'loot', c if c != 'weapon' else 'weapon_' + s
    return {'projectile': 'projectiles', 'npc': 'npcs', 'container': 'containers', 'portal': 'portals'}.get(c, 'other'), 'all'

def safe(s): return re.sub(r'[^\w\-. ]', '_', s or '')[:60]
shutil.rmtree(W('views'), ignore_errors=True)
summary = {}; unmatched_report = []
for dung, srcs in SRCS.items():
    spec = open(W('docs/dungeon_specs', dung + '.md'), encoding='utf-8').read()
    chosen = {}
    def add(r, why):
        k = (r['id'], r['type'], r['category'])  # dedupe the same object found in several files
        if k not in chosen: chosen[k] = (r, why)
    for r in idx:
        if r['src'] in srcs and r['category'] != 'misc': add(r, 'src')
    names_resolved, names_inside, names_missing = [], [], []
    for cands in spec_names(spec):
        got = None
        al = ALIASES.get(dung, {}).get(cands[-1])
        if al:
            hits = [r for r in idx if re.search(al, r['id'] or '') and r['category'] in SPEC_CATS]
            if hits: got = (cands[-1], hits)
        if not got and cands[-1].lower().startswith('epic '): cands = cands + [cands[-1][5:]]  # game display names drop "Epic"
        for q in ([] if got else cands):
            hits = [r for k in (n(q), sing(n(q))) for r in by_name.get(k, []) if r['category'] in SPEC_CATS]
            hits = hits or [r for r in by_group.get(n(q), []) if r['category'] in SPEC_CATS]  # spec names a game Group
            if hits: got = (q, hits); break
        if got:
            q, hits = got
            if all(h['src'] in srcs for h in hits): names_inside.append(q)
            else: names_resolved.append((q, sorted({h['src'] for h in hits})[:4]))
            for h in hits: add(h, 'alias' if ALIASES.get(dung, {}).get(cands[-1]) else 'spec')
            continue
        # not found: suggestions (unverified)
        q = cands[-1]; qt = toks(q); sug = []
        for nm in all_names:
            if qt and qt <= toks(nm) and len(toks(nm)) <= len(qt) + 3: sug.append(nm)
        sug = sug or difflib.get_close_matches(n(q), all_names, n=3, cutoff=0.85)
        sug_src = sorted({(r['id'], r['src']) for nm in sug[:4] for r in by_name[nm] if r['category'] in SPEC_CATS})[:5]
        in_src = any(s in srcs for _, s in sug_src)
        groups = {(i, ) for i, _ in sug_src}
        if len(qt) >= 2 and len(groups) == 1 and not in_src:  # one candidate, two or more words: accept (unverified)
            for nm in sug[:4]:
                for r in by_name[nm]:
                    if r['category'] in SPEC_CATS: add(r, 'spec~')
            names_resolved.append((q + ' (guess)', sorted({s for _, s in sug_src})))
            continue
        if in_src:  # suggestion lives in the dungeon's own file, so the view already holds it
            names_inside.append(q + ' (~' + sug_src[0][0] + ')'); continue
        names_missing.append((q, sug_src, in_src))
    for k, (r, why) in list(chosen.items()):
        if r['category'] in ('enemy', 'npc', 'helper'):
            for pid in projs.get((r['src'], r['id'], r['type']), []):
                for pr in proj_by_id.get(pid, []): add(pr, 'proj')
    loot_text = section(spec, 'Loot')
    for r in loot_recs:
        if loot_hit(loot_text, r['id']): add(r, 'loot')
    ph = hints(spec)
    tile_hints_used = collections.Counter()
    for r in global_tiles:
        h = hint_match(r['id'], ph, PREFIX.get(dung, frozenset()))
        if h: add(r, 'tile'); tile_hints_used[h] += 1
    for r in global_walls:
        h = hint_match(r['id'], ph, PREFIX.get(dung, frozenset()))
        if h: add(r, 'wall'); tile_hints_used[h] += 1
    out = collections.Counter(); entries = []
    for k, (r, why) in chosen.items():
        g, s = group_of(r)
        d = W('views', dung, g, safe(s)); os.makedirs(d, exist_ok=True)
        base = os.path.basename(r['files']['main']); dst = os.path.join(d, base)
        if os.path.exists(dst): dst = os.path.join(d, safe(r['src']) + '__' + base)
        shutil.copyfile(W(r['files']['main']), dst)
        if 'frames' in r['files']:
            fd = os.path.join(d, '_frames'); os.makedirs(fd, exist_ok=True)
            shutil.copyfile(W(r['files']['frames']), os.path.join(fd, os.path.basename(dst)))
        out[g] += 1
        entries.append(dict(id=r['id'], type=r['type'], src=r['src'], category=r['category'], sub=r['sub'], why=why,
                            file=os.path.relpath(dst, W('views', dung)).replace('\\', '/')))
    why_c = collections.Counter(e['why'] for e in entries)
    json.dump(dict(dungeon=dung, sources=srcs, counts=out, why=why_c, tile_hints_used=tile_hints_used,
                   names_in_own_files=names_inside, names_in_other_files=names_resolved,
                   names_not_found=[dict(name=q, suggestions=s, suggestion_in_own_files=i) for q, s, i in names_missing],
                   entries=entries), open(W('views', dung, 'view.json'), 'w'), indent=0)
    summary[dung] = (dict(out), dict(why_c))
    unmatched_report.append((dung, names_resolved, names_missing, tile_hints_used, ph))
    print(f"{dung:30s} {sum(out.values()):5d} why={dict(why_c)} not_found={len(names_missing)}")
with open(W('views', 'README.md'), 'w', encoding='utf-8') as f:
    f.write('# Dungeon views\n\nBuilt by tools/build_dungeon_views.py. Each folder has view.json with the reason (why) for every sprite.\nSee UNMATCHED.md for spec names with no game object.\n\n| Dungeon | Sprites | Groups |\n|---|---|---|\n')
    for d, (o, w) in summary.items(): f.write(f"| {d} | {sum(o.values())} | {', '.join(f'{k} {v}' for k, v in sorted(o.items()))} |\n")
with open(W('views', 'UNMATCHED.md'), 'w', encoding='utf-8') as f:
    f.write('# Spec names and the game data\n\nFor each dungeon: names found only in other game files (added to the view), names with no game object, and tile hints that matched global tiles.\nSuggestions are unverified guesses by word overlap. "(own file)" means the suggestion is already in the view through its own XML.\n')
    for dung, res, miss, th, ph in unmatched_report:
        f.write(f'\n## {dung}\n')
        if res: f.write('- Found in other game files: ' + '; '.join(f"{q} -> {', '.join(s)}" for q, s in res) + '\n')
        if miss:
            f.write('- Not found:\n')
            for q, sug, ins in miss:
                f.write(f"  - {q}" + (f" (suggestions: {', '.join(f'{a} [{b}]' for a, b in sug)}{'; own file' if ins else ''})" if sug else ' (no suggestion)') + '\n')
        f.write(f"- Tile hints: {len(ph)} read; matched global tiles/walls: {dict(th) if th else 'none'}\n")
