"""Build the link-share image, card.png: the top of the page itself at 1200 x 630.
usage: card.py out.png url
Rendered with reduced motion, so the page is finished and the plot is the simulation's
still frame; give the url a ?seed=N so the route is the same on every rebuild."""
import sys
from playwright.sync_api import sync_playwright
out, url = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1200, 'height': 630}, color_scheme='light', reduced_motion='reduce')
    pg.goto(url); pg.wait_for_timeout(800)
    pg.screenshot(path=out)
    b.close()
