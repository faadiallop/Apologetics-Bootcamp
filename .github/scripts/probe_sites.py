"""Probe transcript sites with a headless browser. Prints what each returns; saves screenshots."""
import os, re, sys
from playwright.sync_api import sync_playwright

VID = os.environ["VID"]
URL = f"https://www.youtube.com/watch?v={VID}"
SITES = {
    "miniwebtool": "https://miniwebtool.com/youtube-transcript-generator/",
    "supadata": "https://supadata.ai/youtube-transcript",
    "vidiq": "https://vidiq.com/youtube-transcript-generator/",
}
os.makedirs("shots", exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, site in SITES.items():
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        try:
            pg.goto(site, wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(3000)
            box = pg.locator("input[type=url], input[type=text], input:not([type])").first
            box.fill(URL, timeout=10000)
            btn = pg.get_by_role("button", name=re.compile(r"transcript|get|generate", re.I)).first
            btn.click(timeout=10000)
            pg.wait_for_timeout(15000)
            text = pg.inner_text("body")
            stamps = len(re.findall(r"\b\d{1,2}:\d{2}\b", text))
            print(f"== {name}: body {len(text)} chars, {stamps} timestamp-like marks")
            print(text[:300].replace("\n", " | "))
        except Exception as e:
            print(f"== {name}: FAILED {type(e).__name__}: {str(e)[:200]}")
        pg.screenshot(path=f"shots/{name}.png")
        pg.close()
    b.close()
