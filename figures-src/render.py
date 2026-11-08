"""Render figure sources to PNG (needs: uv run --with playwright playwright install chromium-headless-shell).

    uv run --with playwright python figures-src/render.py figures-src/<name>.html src/assets/weeks/week-NN/<name>.png
"""
import asyncio, sys, pathlib
from playwright.async_api import async_playwright
async def main(src, out):
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(device_scale_factor=1.5)
        await pg.goto(pathlib.Path(src).resolve().as_uri()); await pg.evaluate("document.fonts.ready")
        await pg.locator("svg").first.screenshot(path=out); await b.close()
if len(sys.argv) != 3:
    sys.exit(__doc__)
asyncio.run(main(*sys.argv[1:3]))
