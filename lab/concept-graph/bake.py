"""Compute the concept map's layouts once, offline, and save them (layout.json).

The page then draws fixed positions and never runs a simulation, however large the
graph. Needs a local server on the repo root (./serve.sh) and Playwright.

    python3 lab/concept-graph/bake.py
"""
import asyncio, json, pathlib, time
from playwright.async_api import async_playwright
HERE = pathlib.Path(__file__).resolve().parent

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        t = time.time()
        await pg.goto('http://localhost:8899/lab/concept-graph/?bake=1')
        await pg.wait_for_function('window.__layout', timeout=600000)
        L = await pg.evaluate('window.__layout')
        (HERE / 'layout.json').write_text(json.dumps(L))
        print(f"layout.json: {len(L['web'])} positions per layout, baked in {time.time() - t:.1f} s")
        await b.close()
asyncio.run(main())
