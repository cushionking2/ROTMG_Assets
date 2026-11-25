"""Count asset types per file in the game copy. Usage: python survey_assets.py <Data folder> <out json>"""
import sys, os, json, collections
import UnityPy
data, out = sys.argv[1], sys.argv[2]
res = {}
for n in sorted(os.listdir(data)):
    if n.endswith(('.assets','.resource','.resS','.json','.txt','.info','.config')) or n.startswith(('level','globalgamemanagers')):
        pass
    p = os.path.join(data, n)
    if not os.path.isfile(p) or n.endswith(('.resS','.resource')) or n.endswith(('.json','.txt','.info','.config')): continue
    try:
        env = UnityPy.load(p)
        c = collections.Counter(o.type.name for o in env.objects)
        res[n] = dict(c)
        print(n, dict(c.most_common(8)), flush=True)
    except Exception as e:
        print(n, 'ERR', e, flush=True)
json.dump(res, open(out,'w'), indent=1)
