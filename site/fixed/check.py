#!/usr/bin/env python3
"""Check the fixed-piece files against the layout in README.md.

Run from anywhere: python3 site/fixed/check.py
It reads each group's file the way the site will, and reports what the site
could not serve. It does not judge whether a piece is true or well put.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if os.name == "nt" and not HERE.startswith("\\\\"):
    HERE = "\\\\?\\" + HERE  # paths over 260 characters need this on Windows
VERSION = os.path.join(HERE, "..", "..", "skills", "apologetics-boot-camp", "VERSION")

PARTS = ["opening", "background", "foundation", "know-them", "argument",
         "tactic", "their-answers", "gospel", "bridge"]
TACTICS = ["gather", "burden-of-proof", "rescues", "rescues-professors-ploy",
           "rescues-hot-seat", "staying-on-topic", "steamroller", "lead",
           "turnabout", "suicide", "practical-suicide", "sibling-rivalry",
           "infanticide", "taking-the-roof-off", "unfalsifiable",
           "rhodes-scholar", "just-the-facts"]
FIELDS = ["say", "check", "expect"]
MARKUP = re.compile(r"[*_#`\[\]]|^\s*[-+]\s")


def words(text):
    return len(text.split())


def parse(text):
    """Return (header lines, [(name, body lines)])."""
    header, pieces = [], []
    for line in text.replace("\r\n", "\n").split("\n"):
        if line.startswith("## "):
            pieces.append((line[3:].strip(), []))
        elif pieces:
            pieces[-1][1].append(line)
        else:
            header.append(line)
    return header, pieces


def part_of(name):
    if name in ("opening-beginner", "opening-not-beginner"):
        return "opening"
    if name.startswith("tactic-"):
        return "tactic" if name[len("tactic-"):] in TACTICS else None
    m = re.fullmatch(r"(.+)-(\d+)", name)
    return m.group(1) if m and m.group(1) in PARTS[1:] else None


def check_file(path, stamp):
    errors, notes = [], []
    header, pieces = parse(open(path, encoding="utf-8").read())
    head = [h for h in header if h.strip()]
    if not head or not head[0].startswith("# "):
        errors.append("first line is not a '# ' title")
    status = [h for h in head if h.startswith("Status: ")]
    if len(status) != 1 or status[0] not in ("Status: draft", "Status: approved"):
        errors.append("needs one line 'Status: draft' or 'Status: approved'")
    source = [h for h in head if h.startswith("Source: skill stamp ")]
    if len(source) != 1:
        errors.append("needs one line 'Source: skill stamp <stamp>'")
    elif stamp and source[0].split()[-1] != stamp:
        notes.append("written from skill stamp %s; the skill is now %s, so check the pieces against it"
                     % (source[0].split()[-1], stamp))

    names = [n for n, _ in pieces]
    for n in sorted(set(n for n in names if names.count(n) > 1)):
        errors.append("%s appears more than once" % n)
    for needed in ("opening-beginner", "opening-not-beginner"):
        if needed not in names:
            errors.append("%s is missing" % needed)

    last_part, last_number, last_tactic = 0, {}, -1
    for name, body in pieces:
        part = part_of(name)
        if part is None:
            errors.append("%s is not a piece name the layout allows" % name)
            continue
        if PARTS.index(part) < last_part:
            errors.append("%s is out of order: it comes after a later part" % name)
        last_part = max(last_part, PARTS.index(part))
        text = "\n".join(body).strip()

        if part == "opening":
            if words(text) > 350:
                errors.append("%s is %d words; the limit is 350" % (name, words(text)))
            if MARKUP.search(text):
                errors.append("%s has markup that would be read aloud" % name)
            continue

        if part == "tactic":
            place = TACTICS.index(name[len("tactic-"):])
            if place < last_tactic:
                errors.append("%s is out of the order of the skill's table" % name)
            last_tactic = max(last_tactic, place)
        else:
            number = int(name.rsplit("-", 1)[1])
            if number != last_number.get(part, 0) + 1:
                errors.append("%s is out of sequence" % name)
            last_number[part] = number

        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        found = {}
        for p in paragraphs:
            m = re.match(r"(say|check|expect): (.+)", p, re.S)
            if not m or "\n" in p:
                errors.append("%s has a paragraph that is not one line of say, check or expect" % name)
            elif m.group(1) in found:
                errors.append("%s has two '%s' lines" % (name, m.group(1)))
            else:
                found[m.group(1)] = m.group(2)
        if list(found) != FIELDS:
            errors.append("%s needs say, check and expect, once each and in that order" % name)
            continue
        for field in ("say", "check"):
            if MARKUP.search(found[field]):
                errors.append("%s: '%s' has markup that would be read aloud" % (name, field))
        if part == "tactic" and words(found["say"]) > 100:
            errors.append("%s teaches in %d words; the limit is 100" % (name, words(found["say"])))
    return len(pieces), errors, notes


def main():
    stamp = open(VERSION, encoding="utf-8").read().strip() if os.path.exists(VERSION) else ""
    failed = False
    for path in sorted(glob.glob(os.path.join(HERE, "*.md"))):
        if os.path.basename(path) == "README.md":
            continue
        count, errors, notes = check_file(path, stamp)
        print("%s  %s: %d pieces" % ("FAIL" if errors else "PASS", os.path.basename(path), count))
        for e in errors:
            print("        - " + e)
        for n in notes:
            print("        note: " + n)
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
