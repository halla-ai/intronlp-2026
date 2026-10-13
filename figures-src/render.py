"""Render figure sources to PNG: uv run --with playwright python figures-src/render.py <name.html> <out.png>"""
import asyncio, sys, pathlib
from playwright.async_api import async_playwright
async def main(src, out):
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(device_scale_factor=1.5)
        await pg.goto(pathlib.Path(src).resolve().as_uri()); await pg.wait_for_timeout(500)
        await pg.locator("svg").first.screenshot(path=out); await b.close()
asyncio.run(main(*sys.argv[1:3]))
