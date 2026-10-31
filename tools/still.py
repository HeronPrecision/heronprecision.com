"""Capture the full page once every reveal has finished.
usage: still.py out.png url light|dark WxH settle_ms
Scrolls the whole page first so each section reveals, then returns to the top and waits
settle_ms so the plot is mid-flight rather than mid-draw."""
import sys
from playwright.sync_api import sync_playwright
out, url, scheme, size, settle = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
w, h = (int(x) for x in size.split('x'))
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': w, 'height': h}, color_scheme=scheme)
    pg.goto(url); pg.wait_for_timeout(1200)
    H = pg.evaluate('document.documentElement.scrollHeight')
    for y in range(0, H, h//2): pg.evaluate(f'window.scrollTo(0,{y})'); pg.wait_for_timeout(250)
    pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(settle)
    pg.screenshot(path=out, full_page=True)
    b.close()
