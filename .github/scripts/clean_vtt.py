"""Turn a YouTube .vtt caption file into plain timestamped lines.

Auto-captions repeat each line as the words build up; keep one copy.
Usage: python clean_vtt.py <input.vtt> <output.txt>
"""
import re
import sys

TIME = re.compile(r"^(\d{2}:\d{2}:\d{2})\.\d{3} --> ")
TAG = re.compile(r"<[^>]+>")


def clean(path):
    out, last, stamp = [], "", ""
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            m = TIME.match(line)
            if m:
                stamp = m.group(1)
                continue
            if not line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
                continue
            text = TAG.sub("", line).strip()
            if text and text != last:
                out.append(f"[{stamp}] {text}")
                last = text
    return out


if __name__ == "__main__":
    lines = clean(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{len(lines)} lines written")
