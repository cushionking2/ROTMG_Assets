"""Match each docs/dungeon_specs/*.md to game XML sources by enemy/object names. Prints top sources per dungeon."""
import sys, os, re, json, collections, glob
root = sys.argv[1]
objs = json.load(open(os.path.join(root, 'work/objects.json')))
norm = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower().replace('the ', '', 1) if (s or '').lower().startswith('the ') else re.sub(r'[^a-z0-9]', '', (s or '').lower()))
def n(s): return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()
by_name = collections.defaultdict(list)
for o in objs:
    for nm in (o['id'], o['display']):
        if nm: by_name[n(nm)].append(o)
res = {}
for f in sorted(glob.glob(os.path.join(root, 'docs/dungeon_specs/*.md'))):
    b = os.path.basename(f)
    if b.startswith('_') or b == 'INDEX.md': continue
    t = open(f, encoding='utf-8').read()
    m = re.search(r'## Enemies(.*?)(\n## |\Z)', t, re.S)
    names = []
    if m:
        for line in m.group(1).splitlines():
            if line.startswith('|') and not line.startswith('|---') and not line.lower().startswith('| name'):
                names.append(line.split('|')[1].strip())
    hits = collections.Counter(); found = 0
    for nm in names:
        c = by_name.get(n(nm), [])
        if c: found += 1
        for o in c: hits[o['src']] += 1
    res[b[:-3]] = dict(names=len(names), found=found, top=hits.most_common(4))
    print(f"{b[:-3]:30s} enemies {found}/{len(names)}  {hits.most_common(4)}")
json.dump(res, open(os.path.join(root, 'work/dungeon_match.json'), 'w'), indent=1)
