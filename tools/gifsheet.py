"""Lay out evenly spaced moments of a GIF as one sheet, labeled in seconds, five to a row.
usage: gifsheet.py in.gif out.png [moments, default 10]"""
import sys
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
g = Image.open(src); frames = []; t = 0
try:
    while True:
        frames.append((t, g.convert('RGB').copy())); t += g.info.get('duration', 33); g.seek(g.tell() + 1)
except EOFError: pass
end = frames[-1][0]
picks = [min(frames, key=lambda f: abs(f[0] - end * (i + 0.5) / n)) for i in range(n)]
w, h = picks[0][1].size; cols = 5; rows = (n + cols - 1) // cols
sheet = Image.new('RGB', (cols * (w + 12), rows * (h + 24)), 'white'); d = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(picks):
    x, y = (i % cols) * (w + 12), (i // cols) * (h + 24)
    sheet.paste(im, (x, y + 20)); d.text((x + 2, y + 4), f'{t / 1000:.1f} s', fill='black')
sheet.save(out)
