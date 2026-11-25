"""Export TextAssets and Texture2D from the game copy. Usage: python export_raw.py <Data folder> <out dir>"""
import sys, os, re
import UnityPy
data, out = sys.argv[1], sys.argv[2]
tdir, xdir, sdir = (os.path.join(out, x) for x in ('text', 'textures', 'sprites'))
for d in (tdir, xdir, sdir): os.makedirs(d, exist_ok=True)
def safe(n): return re.sub(r'[^\w.\- ]', '_', n)
seen = {}
def uniq(d, name, ext):
    k = (d, name.lower()+ext); seen[k] = seen.get(k, 0) + 1
    return f"{name}{'' if seen[k]==1 else '_'+str(seen[k])}{ext}"
for fn in ('resources.assets','globalgamemanagers.assets','sharedassets0.assets','sharedassets1.assets','sharedassets3.assets','sharedassets4.assets'):
    env = UnityPy.load(os.path.join(data, fn))
    print(fn, flush=True)
    for o in env.objects:
        t = o.type.name
        try:
            if t == 'TextAsset':
                d = o.read(); b = d.m_Script.encode('utf-8','surrogateescape') if isinstance(d.m_Script,str) else bytes(d.m_Script)
                head = b[:200].lstrip()
                ext = '.xml' if head.startswith(b'<') or head.startswith(b'\xef\xbb\xbf<') else ('.json' if head[:1] in (b'{',b'[') else ('.bin' if b'\x00' in b[:64] else '.txt'))  # .bin: binary data such as spritesheetf
                open(os.path.join(tdir, uniq(tdir, safe(d.m_Name), ext)), 'wb').write(b)
            elif t == 'Texture2D':
                d = o.read(); d.image.save(os.path.join(xdir, uniq(xdir, safe(d.m_Name), '.png')))
            elif t == 'Sprite' and fn == 'resources.assets':
                d = o.read(); d.image.save(os.path.join(sdir, uniq(sdir, safe(d.m_Name), '.png')))
        except Exception as e:
            print('  ERR', t, getattr(o, 'path_id', '?'), e, flush=True)
