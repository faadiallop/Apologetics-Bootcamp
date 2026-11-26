"""Fetch one video's transcript through vidIQ's free transcript page, using a headless browser.

Usage: VID=<11-char id> python fetch_transcript.py <output.txt>
Writes one line per caption segment: [hh:mm:ss] text
Stops with an error if the page shows a human check or returns no transcript.
"""
import os
import re
import sys

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

SITE = "https://vidiq.com/youtube-transcript-generator/"
VID = os.environ["VID"]
OUT = sys.argv[1]


def srt_to_lines(srt):
    lines = []
    for block in re.split(r"\n\s*\n", srt.strip()):
        parts = block.strip().splitlines()
        if len(parts) < 3:
            continue
        m = re.match(r"(\d{2}:\d{2}:\d{2})", parts[1])
        if m:
            lines.append(f"[{m.group(1)}] {' '.join(parts[2:]).strip()}")
    return lines


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(SITE, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(3000)
    page.locator("input[type=url], input[type=text], input:not([type])").first.fill(
        f"https://www.youtube.com/watch?v={VID}", timeout=10000
    )
    page.get_by_role("button", name=re.compile(r"transcript|get|generate", re.I)).first.click(timeout=10000)
    try:
        page.get_by_text("Download .srt").first.wait_for(timeout=90000)
    except PWTimeout:
        page.screenshot(path="failure.png")
        sys.exit("No transcript appeared (a human check, an error, or no captions). See failure.png")
    with page.expect_download(timeout=30000) as dl:
        page.get_by_text("Download .srt").first.click()
    with open(dl.value.path(), encoding="utf-8") as f:
        lines = srt_to_lines(f.read())
    browser.close()

if len(lines) < 20:
    sys.exit(f"Transcript too short ({len(lines)} lines); not saved")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(f"{len(lines)} lines written")
