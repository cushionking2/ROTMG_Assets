"""Labeled contact sheet of every sprite from given game XML sources. python src_sheet.py <root> <out.png> <scale> <src>[,<src>...] [cats]"""
import sys, os, json
from PIL import Image, ImageDraw
root, out, sc, srcs = sys.argv[1], sys.argv[2], int(sys.argv[3]), set(sys.argv[4].split(','))
cats = set(sys.argv[5].split(',')) if len(sys.argv) > 5 else None
idx = [r for r in json.load(open(os.path.join(root, 'assets/index.json'))) if r['src'] in srcs and (cats is None or r['category'] in cats)]
items = []
for r in idx:
    im = Image.open(os.path.join(root, r['files']['main'])).convert('RGBA')
    if im.getbbox() is None: continue
    items.append((r, im))
cell = 20 * sc; cols = 8; rows = (len(items) + cols - 1) // cols
sheet = Image.new('RGBA', (cols * cell, rows * (cell + 14)), (60, 60, 60, 255)); dr = ImageDraw.Draw(sheet)
for i, (r, im) in enumerate(items):
    s = im.resize((im.width * sc, im.height * sc), Image.NEAREST); s.thumbnail((cell, cell))
    x, y = (i % cols) * cell, (i // cols) * (cell + 14)
    sheet.alpha_composite(s, (x + (cell - s.width) // 2, y + (cell - s.height) // 2))
    dr.text((x + 1, y + cell), (r['id'] or '')[:18], fill=(255, 255, 255, 255))
sheet.save(out); print(len(items), sheet.size)
