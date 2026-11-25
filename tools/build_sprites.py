"""Crop sprites from the game atlases, sort them by category, and write assets/index.json.

Usage: python -I build_sprites.py <D_Sim root>
Needs: work/objects.json (parse_objects.py), work/raw_export/text/spritesheetf.bin, work/raw_export/textures/*.png
Rules found by inspection (see docs/EXTRACTION_PLAN.md):
  static sprite  : sheet record with f3 == XML <Index> (no f3 -> index 0). rect is (x,y,w,h) in the atlas.
                   f7 == 1 means the rect has 1 px padding on each side (crop inset by 1).
  animated sprite: records of the second root vector with sheet == <File> and f1 == <Index>, in file order.
  atlas          : f7 == 1 -> groundTiles.png, 2 -> characters.png, 4 -> mapObjects.png. y axis is top-down as saved by UnityPy.
"""
import sys, os, re, json, collections
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ssf

root = sys.argv[1]
W = lambda *p: os.path.join(root, *p)
objs = json.load(open(W('work', 'objects.json')))
static = ssf.load(W('work/raw_export/text/spritesheetf.bin'))
frames = ssf.load_frames(W('work/raw_export/text/spritesheetf.bin'))
atlas = {n: Image.open(W('work/raw_export/textures', n + '.png')).convert('RGBA') for n in ('mapObjects', 'characters', 'groundTiles')}
ATLAS = {1: 'groundTiles', 2: 'characters', 4: 'mapObjects'}

static_ix = {}
for sh, v in static.items():
    static_ix[sh] = {(s['f3'] or 0): s for s in v['sprites']}
frame_ix = collections.defaultdict(lambda: collections.defaultdict(list))
for r in frames:
    frame_ix[r['sheet']][r['f1']].append(r)

def crop_static(ref):
    if not ref: return None
    s = static_ix.get(ref['file'], {}).get(ref['index'])
    if s is None or not s['rect']: return None
    x, y, w, h = (int(v) for v in s['rect'])
    if s['f7'] == 1: x, y, w, h = x + 1, y + 1, w - 2, h - 2
    return atlas[ATLAS.get(s['f7'], 'mapObjects')].crop((x, y, x + w, y + h))

def crop_frames(ref):
    if not ref: return None
    fl = frame_ix.get(ref['file'], {}).get(ref['index'])
    if not fl: return None
    out = []
    for r in fl:
        x, y, w, h = (int(v) for v in r['rect'])
        out.append((atlas[ATLAS.get(r['f7'], 'mapObjects')].crop((x, y, x + w, y + h)), r['f4']))
    return out

WEAPON_SUB = ['SWORD', 'DAGGER', 'BOW', 'STAFF', 'WAND', 'KATANA']
ARMOR_SUB = ['LEATHER', 'HEAVY', 'ROBE']
HELPER_RULES = [  # first match wins; tested on the object id and the display name
    ('loot_marker', r'\b(loot|xp|complete|chest|token|balloon|exalt|reward)\b'),
    ('spawner', r'\b(spawner|summoner|controller|dropper|opener|generator|checker|trigger|revealer|wanderer|portal|system)\b'),
    ('effect', r'\b(beam|strike|telegraph|telegrapher|bullet|blast|explosion|wave|meteor|spike|spark|burst|impact|bolt|power|lightning|flame|shot|missile|bomb|split)\b'),
    ('anchor', r'\b(anchor|target|pivot|point|clone|helper|border|bord|map|altar|decor|ritual|indicator|switch|barrel|rock)\b'),
]
LOOT_NAME = re.compile(r'\b(loot|xp|complete)\b', re.I)
def helper_kind(o):
    name = ((o['id'] or '') + ' ' + (o['display'] or '')).lower()
    if (o['tex'] or o['anim'] or {}).get('file') == 'invisible': return 'invisible'
    for kind, pat in HELPER_RULES:
        if re.search(pat, name): return kind
    return 'other'

def categorize(o):
    cls, lab = o['cls'], set(o['labels'])
    if o['tag'] == 'Ground': return 'tile', o['src']
    if cls == 'Equipment' or o['item']:
        for k, subs in (('WEAPON', WEAPON_SUB), ('ARMOR', ARMOR_SUB)):
            if k in lab: return k.lower(), next((s.lower() for s in subs if s in lab), 'other')
        for k in ('ABILITY', 'RING', 'CONSUMABLE'):
            if k in lab: return k.lower(), 'all'
        return 'item_other', 'all'
    if cls == 'Player' or o['player']: return 'player', 'all'
    if cls == 'Skin': return 'skin', 'all'
    if cls == 'Projectile': return 'projectile', 'all'
    if cls in ('Pet',): return 'pet', 'all'
    if cls == 'PetSkin': return 'pet_skin', 'all'
    if o['enemy'] or 'ENEMY' in lab:
        fl = set(o['flags'])
        if 'Invincible' in fl or not (o['hp'] or 0) > 0 or (o['src'] == 'moonlightVillageObjects' and LOOT_NAME.search(o['id'] or '')):
            return 'helper', helper_kind(o)  # no HP, invulnerable, or a loot marker: a mechanic object, not a combatant
        if 'BOSS' in lab: return 'enemy', 'boss'
        if 'MINIBOSS' in lab: return 'enemy', 'miniboss'
        if 'BOSS_SPAWNED' in lab: return 'enemy', 'boss_minion'
        if 'HealthBarBoss' in fl or 'Quest' in fl: return 'enemy', 'event_boss'  # realm event and encounter bosses
        return 'enemy', 'regular'
    if cls == 'Character': return 'npc', 'all'
    if cls in ('Wall', 'ConnectedWall', 'CaveWall', 'DoubleWall'): return 'wall', o['src']
    if cls == 'GameObject': return 'prop', o['src']
    if cls in ('Container',): return 'container', 'all'
    if cls in ('Portal', 'Entrance'): return 'portal', 'all'
    if cls == 'Gravestone': return 'gravestone', 'all'
    return 'misc', (cls or 'none')

def safe(s): return re.sub(r'[^\w\-. ]', '_', s or 'noname').strip()[:80]
used = set(); index = []; miss = collections.Counter(); counts = collections.Counter()
for o in objs:
    cat, sub = categorize(o)
    name = safe(o['id'] or o['type'])
    base = f"{name}__{(o['type'] or '').replace('0x','')}"
    d = os.path.join('assets', cat, safe(sub)); os.makedirs(W(d), exist_ok=True)
    key = (d, base.lower())
    if key in used: base += '_' + safe(o['src'])
    used.add((d, base.lower()))
    rec = dict(id=o['id'], type=o['type'], src=o['src'], category=cat, sub=sub, cls=o['cls'], tier=o['tier'], slot=o['slot'],
               stats=dict(hp=o['hp'], exp=o['exp'], defense=o['defense'], proj=len(o['proj']), flags=o['flags']),
               labels=o['labels'], tex=o['tex'], anim=o['anim'], files={})
    ok = False
    anim_ref = o['anim'] or next((r for r in (o['rand'] or []) if r.get('animated')), None)
    static_ref = o['tex'] or next((r for r in (o['rand'] or []) if not r.get('animated')), None)
    if o['rand'] and len(o['rand']) > 1: rec['variants'] = len(o['rand'])
    if anim_ref:
        fr = crop_frames(anim_ref)
        if fr:
            cw = max(f.width for f, _ in fr); ch = max(f.height for f, _ in fr)
            cols = 6; rows = (len(fr) + cols - 1) // cols
            sheet = Image.new('RGBA', (cols * cw, rows * ch))
            for i, (f, _) in enumerate(fr): sheet.paste(f, ((i % cols) * cw, (i // cols) * ch))
            os.makedirs(W(d, '_frames'), exist_ok=True)
            p = os.path.join(d, '_frames', base + '.png'); sheet.save(W(p)); rec['files']['frames'] = p
            rec['frame_types'] = [t for _, t in fr]
            # preview: first 'stand' (f4 == 0) frame of the second group when 3 groups exist, else of the first
            groups = [fr[i:i + 6] for i in range(0, len(fr), 6)]
            g = groups[1] if len(groups) >= 3 else groups[0]
            pv = next((f for f, t in g if t == 0), g[0][0])
            p = os.path.join(d, base + '.png'); pv.save(W(p)); rec['files']['main'] = p; ok = True
        else: miss['anim:' + (anim_ref['file'])] += 1
    if not ok:
        for key_, ref in (('main', static_ref),):
            im = crop_static(ref)
            if im is not None:
                p = os.path.join(d, base + '.png'); im.save(W(p)); rec['files']['main'] = p; ok = True
            elif ref: miss['static:' + ref['file']] += 1
        if o['top']:
            im = crop_static(o['top'])
            if im is not None:
                p = os.path.join(d, base + '_top.png'); im.save(W(p)); rec['files']['top'] = p
    if o['portrait']:
        pass
    counts[(cat, ok)] += 1
    if ok: index.append(rec)
json.dump(index, open(W('assets', 'index.json'), 'w'), indent=0)
print('indexed', len(index), 'of', len(objs))
for (c, ok), n in sorted(counts.items()): print(f'  {c:12s} {"ok" if ok else "NO SPRITE":10s} {n}')
print('misses', miss.most_common(15))
