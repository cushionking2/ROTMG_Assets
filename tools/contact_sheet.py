"""Contact sheet from assets/index.json. python contact_sheet.py <root> <out.png> <category> [sub] [n] [scale] [label_filter_substr]"""
import sys, os, json, random
from PIL import Image, ImageDraw
root, out, cat = sys.argv[1:4]
sub = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != '-' else None
n = int(sys.argv[5]) if len(sys.argv) > 5 else 80
sc = int(sys.argv[6]) if len(sys.argv) > 6 else 4
idx = [r for r in json.load(open(os.path.join(root, 'assets/index.json'))) if r['category'] == cat and (sub is None or r['sub'] == sub)]
random.seed(1); random.shuffle(idx); idx = idx[:n]
cell = 20 * sc; cols = 10; rows = (len(idx) + cols - 1) // cols
im = Image.new('RGBA', (cols * cell, rows * (cell + 12)), (60, 60, 60, 255)); dr = ImageDraw.Draw(im)
for i, r in enumerate(idx):
    s = Image.open(os.path.join(root, r['files']['main'])).convert('RGBA'); s = s.resize((s.width * sc, s.height * sc), Image.NEAREST)
    s.thumbnail((cell, cell)); x, y = (i % cols) * cell, (i // cols) * (cell + 12)
    im.alpha_composite(s, (x + (cell - s.width) // 2, y + (cell - s.height) // 2)); dr.text((x + 1, y + cell), (r['id'] or '')[:14], fill=(255, 255, 255, 255))
im.save(out); print(len(idx), im.size)
