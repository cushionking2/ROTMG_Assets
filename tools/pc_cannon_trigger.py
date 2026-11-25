"""Pirate Cave: when do the boss ship cannons start firing? Prints boss HP samples and cannon shot times per run (seconds from the first event).
Result (2026-11-21): first shot comes about 3 to 4 s after boss HP drops below roughly 50 percent. Run: python -I tools/pc_cannon_trigger.py"""
import json,glob,os,sys
OBJ={}
for x in json.load(open('work/objects.json')):
    if x['tag']=='Object':
        try: OBJ[int(x['type'],16)]=x
        except: pass
CAN='PC Dreadstump Cannon'; BOSS='Dreadstump the Pirate King'
for f in sorted(glob.glob('collector/captures/*Pirate_Cave.events.jsonl')):
    cans=set(); boss=None; maxhp=None; hp=[]; shots=[]; dmg=[]; t0=None; drop=None; ticks=[]
    for l in open(f):
        r=json.loads(l)
        if t0 is None: t0=r['t']
        if r['k']=='upd':
            for oid,t,x,y,st in r['new']:
                n=OBJ.get(t,{}).get('id')
                if n==CAN: cans.add(oid)
                if n==BOSS:
                    boss=oid
                    d=dict((a,b) for a,b in st)
                    if 0 in d: maxhp=d[0]
                    if 1 in d: hp.append((r['t'],d[1],'upd'))
            if boss in r['drop']: drop=r['t']
        elif r['k']=='tick':
            for oid,x,y,st in r['s']:
                if oid==boss:
                    for sn,sv in st:
                        if sn==1: hp.append((r['t'],sv,'tick'))
                        if sn==0: maxhp=sv
        elif r['k']=='eshoot' and r['owner'] in cans: shots.append(r['t'])
        elif r['k']=='dmg' and r['target']==boss: dmg.append((r['t'],r['amt']))
    print(os.path.basename(f)[9:15],'maxhp',maxhp,'boss HP samples',[(round((t-t0)/1000),v) for t,v,_ in hp][:16],'cannon shots at s',sorted(set(round((s-t0)/1000) for s in shots))[:6],'dmg events on boss',len(dmg),'drop',None if drop is None else round((drop-t0)/1000))
