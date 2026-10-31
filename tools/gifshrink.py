"""Shrink a GIF: gifshrink.py in.gif out.gif [scale=0.75] [keep every Nth frame=2] [colors=64].
Dropped frames add their time to the frame before, so the length is unchanged."""
import sys
from PIL import Image, ImageSequence
src, dst = sys.argv[1], sys.argv[2]
sc, step, cols = (float(sys.argv[3]) if len(sys.argv) > 3 else 0.75), (int(sys.argv[4]) if len(sys.argv) > 4 else 2), (int(sys.argv[5]) if len(sys.argv) > 5 else 64)
g = Image.open(src); fr=[]; du=[]
for i, f in enumerate(ImageSequence.Iterator(g)):
    d = f.info.get('duration', 40)
    if i % step: du[-1] += d; continue
    im = f.convert('RGB'); im = im.resize((round(im.width*sc), round(im.height*sc)), Image.LANCZOS)
    fr.append(im.quantize(cols, method=Image.MEDIANCUT)); du.append(d)
fr[0].save(dst, save_all=True, append_images=fr[1:], duration=du, loop=0, optimize=True)
