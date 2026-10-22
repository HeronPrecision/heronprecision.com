"""Record a page's real-time motion as a GIF via Chromium's screencast.
usage: cast.py out.gif url light|dark seconds WxH scale [scroll_px] [x,y,w,h crop in CSS px] [clicks]
clicks: "ms:x,y;ms:x,y" -- clicks at those page coordinates, timed from load.
  "ms:~x,y" glides the pointer there over 600 ms without clicking; "ms:^px" scrolls
  the page to px smoothly. Actions start once the page has loaded."""
import sys, io, base64, time
from playwright.sync_api import sync_playwright
from PIL import Image
out, url, scheme, secs = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
w, h = (int(x) for x in sys.argv[5].split('x')); scale = float(sys.argv[6])
scroll = int(sys.argv[7]) if len(sys.argv) > 7 else 0
crop = tuple(int(v) for v in sys.argv[8].split(',')) if len(sys.argv) > 8 and sys.argv[8] else None
clicks = [(int(c.split(':')[0]), c.split(':', 1)[1]) for c in sys.argv[9].split(';')] if len(sys.argv) > 9 else []
frames = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': w, 'height': h}, color_scheme=scheme)
    cdp = pg.context.new_cdp_session(pg)
    def on_frame(e):
        frames.append((time.monotonic(), e['data']))
        try: cdp.send('Page.screencastFrameAck', {'sessionId': e['sessionId']})
        except Exception: pass  # a frame can arrive after the browser closes
    cdp.on('Page.screencastFrame', on_frame)
    cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 85, 'everyNthFrame': 1})
    pg.goto(url, wait_until='commit')
    if scroll:
        pg.wait_for_timeout(int(secs * 550))
        pg.evaluate(f"window.scrollTo({{top:{scroll},behavior:'smooth'}})")
        pg.wait_for_timeout(int(secs * 450))
    else:
        t = 0
        for ms, a in sorted(clicks):
            pg.wait_for_timeout(max(0, ms - t)); t = ms
            if a[0] == '^':
                pg.evaluate(f"window.scrollTo({{top:{int(a[1:])},behavior:'smooth'}})")
                continue
            x, y = map(float, a.lstrip('~').split(','))
            if a[0] == '~':
                pg.mouse.move(x, y, steps=36); t += 600
            else:
                pg.mouse.move(x, y, steps=8); pg.mouse.click(x, y)
        pg.wait_for_timeout(max(0, int(secs * 1000) - t))
    cdp.send('Page.stopScreencast'); b.close()
frames.sort()
# resample to a steady 30 fps so the GIF plays at true speed
t0, t1 = frames[0][0], frames[-1][0]; step = 1/30; out_frames = []; j = 0; t = t0
while t <= t1:
    while j + 1 < len(frames) and frames[j+1][0] <= t: j += 1
    out_frames.append(j); t += step
cache = {}
def img(j):
    if j not in cache:
        im = Image.open(io.BytesIO(base64.b64decode(frames[j][1]))).convert('RGB')
        if crop:
            k = im.width / w
            im = im.crop(tuple(int(v * k) for v in (crop[0], crop[1], crop[0] + crop[2], crop[1] + crop[3])))
        cache[j] = im.resize((int(im.width*scale), int(im.height*scale)), Image.LANCZOS).convert('P', palette=Image.ADAPTIVE, colors=96)
    return cache[j]
# collapse identical consecutive indices into longer durations
seq = []
for j in out_frames:
    if seq and seq[-1][0] == j: seq[-1][1] += 33
    else: seq.append([j, 33])
seq[-1][1] += 1500
ims = [img(j) for j, _ in seq]
ims[0].save(out, save_all=True, append_images=ims[1:], duration=[d for _, d in seq], loop=0, optimize=True)
print(len(frames), 'source frames over', round(t1-t0, 2), 's ->', len(seq), 'gif frames')
