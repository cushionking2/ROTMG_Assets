"""Parse all game XML in raw_export/text into work/objects.json. python parse_objects.py <text dir> <out json>"""
import sys, os, json, re, collections
import xml.etree.ElementTree as ET
tdir, out = sys.argv[1], sys.argv[2]
def tex(el):
    if el is None: return None
    f = el.findtext('File'); i = el.findtext('Index')
    if f is None or i is None: return None
    try: idx = int(i.strip(), 0)
    except ValueError: return None
    return dict(file=f.strip(), index=idx)
FLAGS = ['Quest', 'HealthBarBoss', 'Invincible', 'NoMiniMap', 'TrackLoot', 'God', 'Hero', 'EventChestBoss', 'Encounter', 'Static', 'DrawOnGround', 'Flying', 'StasisImmune']
def num(el, tag):
    try: return float((el.findtext(tag) or '').strip())
    except ValueError: return None
objs = []; bad = []
for fn in sorted(os.listdir(tdir)):
    if not fn.endswith('.xml'): continue
    raw = open(os.path.join(tdir, fn), 'rb').read().decode('utf-8-sig', 'replace')
    raw = re.sub(r'^<\?xml[^>]*\?>', '', raw.lstrip())
    try: root = ET.fromstring(raw)
    except ET.ParseError as e:
        # try wrapping multiple roots
        try: root = ET.fromstring('<R>' + raw + '</R>')
        except ET.ParseError as e2: bad.append((fn, str(e2))); continue
    for el in root.iter():
        if el.tag not in ('Object', 'Ground', 'Tile') or el.get('id') is None and el.get('type') is None: continue
        o = dict(src=fn[:-4], tag=el.tag, id=el.get('id'), type=el.get('type'), cls=el.findtext('Class'), display=el.findtext('DisplayId'), group=el.findtext('Group'),
                 slot=el.findtext('SlotType'), tier=el.findtext('Tier'),
                 labels=[x.strip() for x in (el.findtext('Labels') or '').split(',') if x.strip()],
                 enemy=el.find('Enemy') is not None, item=el.find('Item') is not None, player=el.find('Player') is not None,
                 god=el.find('God') is not None, skin=el.find('Skin') is not None,
                 tex=tex(el.find('Texture')), anim=tex(el.find('AnimatedTexture')),
                 rand=[dict(tex(r), animated=(r.tag == 'AnimatedTexture')) for r in list(el.findall('RandomTexture/Texture')) + list(el.findall('RandomTexture/AnimatedTexture')) if tex(r)] or None,
                 top=tex(el.find('Top')), portrait=tex(el.find('Portrait/AnimatedTexture') if el.find('Portrait/AnimatedTexture') is not None else el.find('Portrait/Texture')),
                 proj=[ (p.get('id'), p.findtext('ObjectId')) for p in el.findall('Projectile')],
                 hp=num(el, 'MaxHitPoints'), exp=num(el, 'Exp'), defense=num(el, 'Defense'),
                 flags=[f for f in FLAGS if el.find(f) is not None],
                 nextra=[c.tag for c in el][:0])
        objs.append(o)
json.dump(objs, open(out, 'w'))
print(len(objs), 'objects; bad files:', bad)
print('by tag', collections.Counter(o['tag'] for o in objs))
print('by class', collections.Counter(o['cls'] for o in objs).most_common(30))
lab = collections.Counter(l for o in objs for l in o['labels']); print('labels', lab.most_common(80))
print('has tex', sum(1 for o in objs if o['tex']), 'anim', sum(1 for o in objs if o['anim']), 'neither', sum(1 for o in objs if not o['tex'] and not o['anim'] and not o['rand']))
