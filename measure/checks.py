#!/usr/bin/env python3
"""Script checks for the boot camp measure.

Run from anywhere:  python3 measure/checks.py [--json] [--saved DIR] [--kjv FILE] [--stamp]

Each check reads the repo as it stands and reports PASS, FAIL, INSPECT or SKIP.
FAIL means something is wrong and the run exits with status 1. INSPECT lists
things a script cannot judge, for a person to look at. Standard library only.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Windows refuses paths over 260 characters unless they carry this prefix, and a
# clone in a deeply nested folder goes over that.
if os.name == "nt" and not ROOT.startswith("\\\\"):
    ROOT = "\\\\?\\" + ROOT
SKILL = os.path.join(ROOT, "skills", "apologetics-boot-camp")
SOPS = os.path.join(SKILL, "sops")
FIXED = os.path.join(SKILL, "fixed")
HERE = os.path.join(ROOT, "measure")

# The King James text the quotations are checked against: one fixed version of a
# public copy, verified by checksum so the weight cannot change unnoticed.
KJV_URL = ("https://raw.githubusercontent.com/thiagobodruk/bible/"
           "4c8b8a4a7bd75fee381e1b55523b152191d6a1a5/json/en_kjv.json")
KJV_SHA256 = "f627b3c24a617013a4514ab24b6dd1bb305b09af237994c018f74cb9c7e71f41"
KJV_CACHE = os.path.join(HERE, ".cache", "en_kjv.json")

BOOKS = [
    ("Genesis", "Gen"), ("Exodus", "Exod"), ("Leviticus", "Lev"), ("Numbers", "Num"),
    ("Deuteronomy", "Deut"), ("Joshua", "Josh"), ("Judges", "Judg"), ("Ruth", "Ruth"),
    ("1 Samuel", "1 Sam"), ("2 Samuel", "2 Sam"), ("1 Kings", "1 Kings"), ("2 Kings", "2 Kings"),
    ("1 Chronicles", "1 Chron"), ("2 Chronicles", "2 Chron"), ("Ezra", "Ezra"),
    ("Nehemiah", "Neh"), ("Esther", "Esth"), ("Job", "Job"), ("Psalms", "Ps"),
    ("Proverbs", "Prov"), ("Ecclesiastes", "Eccl"), ("Song of Solomon", "Song"),
    ("Isaiah", "Isa"), ("Jeremiah", "Jer"), ("Lamentations", "Lam"), ("Ezekiel", "Ezek"),
    ("Daniel", "Dan"), ("Hosea", "Hos"), ("Joel", "Joel"), ("Amos", "Amos"),
    ("Obadiah", "Obad"), ("Jonah", "Jonah"), ("Micah", "Mic"), ("Nahum", "Nah"),
    ("Habakkuk", "Hab"), ("Zephaniah", "Zeph"), ("Haggai", "Hag"), ("Zechariah", "Zech"),
    ("Malachi", "Mal"), ("Matthew", "Matt"), ("Mark", "Mark"), ("Luke", "Luke"),
    ("John", "John"), ("Acts", "Acts"), ("Romans", "Rom"), ("1 Corinthians", "1 Cor"),
    ("2 Corinthians", "2 Cor"), ("Galatians", "Gal"), ("Ephesians", "Eph"),
    ("Philippians", "Phil"), ("Colossians", "Col"), ("1 Thessalonians", "1 Thess"),
    ("2 Thessalonians", "2 Thess"), ("1 Timothy", "1 Tim"), ("2 Timothy", "2 Tim"),
    ("Titus", "Titus"), ("Philemon", "Philem"), ("Hebrews", "Heb"), ("James", "Jas"),
    ("1 Peter", "1 Pet"), ("2 Peter", "2 Pet"), ("1 John", "1 John"), ("2 John", "2 John"),
    ("3 John", "3 John"), ("Jude", "Jude"), ("Revelation", "Rev"),
]
ONE_CHAPTER = {"Obadiah", "Philemon", "2 John", "3 John", "Jude"}
EXTRA_NAMES = {"Psalm": "Psalms", "Song": "Song of Solomon"}


def build_book_regex():
    names = {}
    for full, abbr in BOOKS:
        names[full] = full
        names[abbr] = full
    names.update(EXTRA_NAMES)
    # Longest first, so "1 John" wins over "John" and "Philem" over "Phil".
    alts = sorted(names, key=len, reverse=True)
    pattern = "|".join(re.escape(a) for a in alts)
    return names, r"(?<![\w.])(?<!\d )(?P<book>" + pattern + r")\.?"


BOOK_NAMES, BOOK_RE = build_book_regex()
VERSES = r"\d+(?:[–-]\d+)?(?:,\s*\d+(?:[–-]\d+)?)*"
PART = r"\d+(?!,\d{3}\b)(?::\d+[–-]\d+:\d+|:" + VERSES + r")?"
REF_RE = re.compile(BOOK_RE + r"\s+(?P<list>" + PART + r"(?:;\s*\d+:(?:\d+[–-]\d+:\d+|" + VERSES + r"))*)")


class Report:
    def __init__(self):
        self.rows = []

    def add(self, status, name, detail, items=None):
        self.rows.append({"status": status, "check": name, "detail": detail, "items": items or []})

    def failed(self):
        return any(r["status"] == "FAIL" for r in self.rows)

    def print(self):
        for r in self.rows:
            print(f"{r['status']:8}{r['check']}: {r['detail']}")
            for item in r["items"]:
                print(f"          - {item}")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def rel(path):
    return os.path.relpath(path, ROOT)


def read_split(stem):
    """The response bank and the training plans are each kept as one shared file
    (`stem.md`) and one file for each group (`stem-<group>.md`), so that a
    session loads only its own group's. Read them as one text, the shared file first."""
    parts = sorted(glob.glob(os.path.join(SOPS, stem + "-*.md")))
    return "\n".join(read(p) for p in [os.path.join(SOPS, stem + ".md")] + parts)


def body_of(text):
    """A SKILL.md without its frontmatter."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


# ---------------------------------------------------------------- KJV text

def load_kjv(path=None):
    path = path or KJV_CACHE
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with urllib.request.urlopen(KJV_URL, timeout=120) as resp:
            data = resp.read()
        with open(path, "wb") as f:
            f.write(data)
    with open(path, "rb") as f:
        data = f.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != KJV_SHA256:
        raise ValueError(f"the King James text at {path} does not match its checksum")
    books = json.loads(data.decode("utf-8-sig"))
    if len(books) != 66:
        raise ValueError("the King James text does not hold 66 books")
    return {full: books[i]["chapters"] for i, (full, _) in enumerate(BOOKS)}


def norm(s):
    s = s.lower().replace("’", "'")
    s = re.sub(r"[^a-z' ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def whole_text(kjv):
    return " ".join(norm(re.sub(r"[{}]", "", v)) for full, _ in BOOKS for ch in kjv[full] for v in ch)



# ---------------------------------------------------------------- spoken references

# The fixed pieces are read aloud, so they give references as people say them
# ("Isaiah eight, verse twenty"). These are turned into figures before the
# quotation and reference checks read them, so the same checks cover them.
SMALL = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
         "eighteen", "nineteen"]
TENS = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
_small = "|".join(sorted(SMALL[1:], key=len, reverse=True))
_tens = "(?:" + "|".join(TENS) + r")(?:-(?:" + "|".join(SMALL[1:10]) + "))?"
_under100 = "(?:" + _tens + "|" + _small + ")"
NUM = r"(?:(?:a|one) hundred(?:(?: and)? " + _under100 + ")?|" + _under100 + ")"
ORDINAL = {"First": "1", "Second": "2", "Third": "3"}


def number(phrase):
    """'one hundred and nineteen' -> 119"""
    total = 0
    for w in phrase.replace("-", " ").split():
        if w == "and":
            continue
        if w == "a":
            total += 1
        elif w == "hundred":
            total *= 100
        elif w in TENS:
            total += 20 + 10 * TENS.index(w)
        else:
            total += SMALL.index(w)
    return total


def build_spoken_regex():
    names = set()
    for full, _ in BOOKS:
        m = re.match(r"([123]) (.+)", full)
        names.add(("(?:First|Second|Third) " + re.escape(m.group(2))) if m else re.escape(full))
    names.add("Psalm")
    book = "(?P<book>" + "|".join(sorted(names, key=len, reverse=True)) + ")"
    verses = (r"(?:,|:)? verses? (?P<v1>" + NUM + r")(?:(?P<join>,? and | to | through )(?P<v2>" + NUM + "))?")
    return re.compile(r"\b" + book + r"(?: chapter)? (?P<ch>" + NUM + r")\b(?:" + verses + r")?(?![\w-])")


SPOKEN_RE = build_spoken_regex()


def figures(text):
    """Write each spoken reference in text as figures, keeping the line breaks."""
    def sub(m):
        book = m.group("book")
        first = book.split(" ", 1)[0]
        if first in ORDINAL:
            book = ORDINAL[first] + " " + book.split(" ", 1)[1]
        ref = f"{book} {number(m.group('ch'))}"
        if m.group("v1"):
            ref += f":{number(m.group('v1'))}"
            if m.group("v2"):
                sep = ", " if "and" in m.group("join") else "–"
                ref += sep + str(number(m.group("v2")))
        return ref
    return SPOKEN_RE.sub(sub, text)

# ---------------------------------------------------------------- the files

def prose_files():
    """Every file whose Scripture is meant to be King James."""
    files = sorted(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md")))
    files += sorted(glob.glob(os.path.join(SOPS, "*.md")))
    files += sorted(glob.glob(os.path.join(FIXED, "*.md")))
    files += sorted(glob.glob(os.path.join(ROOT, "site", "prompts", "*.md")))
    for name in ("README.md", "CLAUDE.md", os.path.join("measure", "README.md")):
        path = os.path.join(ROOT, name)
        if os.path.exists(path):
            files.append(path)
    return files


def read_prose(path):
    """A file's text as the checks read it: the fixed pieces with their spoken
    references written as figures."""
    text = read(path)
    return figures(text) if os.path.dirname(os.path.abspath(path)) == os.path.abspath(FIXED) else text


def allowed_strings():
    """Quoted strings that carry a Bible reference but are not King James quotations."""
    path = os.path.join(HERE, "not-kjv-quotations.md")
    if not os.path.exists(path):
        return set()
    return set(re.findall(r'^- "(.*)"\s*$', read(path), flags=re.M))


# ---------------------------------------------------------------- checks

def check_quotations(report, kjv):
    """Two passes. A quoted line followed by its reference in brackets must match
    the King James text, or the check fails. A quoted line that comes after a
    reference in the same sentence is only listed for a person to look at, since
    a script cannot tell whether it was meant as a quotation."""
    whole = whole_text(kjv)
    allowed = allowed_strings()
    good, bad, near, used = 0, [], [], set()

    def matches(quote):
        parts = [norm(p) for p in re.split(r"…|\.\.\.|\[[^\]]*\]", quote)]
        parts = [p for p in parts if len(p.split()) >= 2]
        return bool(parts) and all(p in whole for p in parts)

    for path in prose_files():
        text = read_prose(path)
        for m in re.finditer(r'"([^"\n]{6,400})"', text):
            quote = m.group(1)
            line = text.count("\n", 0, m.start()) + 1
            after = text[m.end():m.end() + 120].lstrip(" ,.;:*_")
            paren = after[1:after.find(")")] if after.startswith("(") and ")" in after else ""
            if paren and REF_RE.match(paren.lstrip("*_ ")):
                if re.search(r"\b(NWT|JPS)\b|citing", paren):
                    continue  # the other group's own edition, or someone else's citation
                if quote in allowed:
                    used.add(quote)
                elif matches(quote):
                    good += 1
                else:
                    bad.append(f'{rel(path)}:{line} "{quote}" ({paren[:40]})')
                continue
            before = re.split(r"[.!?|]\s|\n", text[max(0, m.start() - 110):m.start()])[-1]
            if REF_RE.search(before):
                if quote in allowed:
                    used.add(quote)
                elif matches(quote):
                    good += 1
                else:
                    near.append(f'{rel(path)}:{line} {before.strip()[-40:]} "{quote}"')
    stale = sorted(allowed - used)
    detail = (f"{good} quotations match the King James text word for word; "
              f"{len(used)} quoted lines are listed as not quotations; {len(bad)} do not match")
    report.add("FAIL" if bad else "PASS", "kjv-quotations", detail, bad)
    if near:
        report.add("INSPECT", "kjv-quotations", "quoted after a reference, and not King James wording", near)
    if stale:
        report.add("INSPECT", "kjv-quotations", "listed in not-kjv-quotations.md but no longer in the text",
                   [f'"{x}"' for x in stale])


def parse_list(book, text):
    """Yield (chapter, verse) pairs, verse None for a whole chapter."""
    single = book in ONE_CHAPTER
    for part in re.split(r";\s*", text):
        m = re.fullmatch(r"(\d+):(\d+)[–-](\d+):(\d+)", part)
        if m:
            yield int(m.group(1)), int(m.group(2))
            yield int(m.group(3)), int(m.group(4))
            continue
        if ":" in part:
            chapter, verses = part.split(":", 1)
            chapter = int(chapter)
        elif single:
            chapter, verses = 1, part
        else:
            yield int(part), None
            continue
        for piece in re.split(r",\s*", verses):
            for v in re.split(r"[–-]", piece):
                yield chapter, int(v)


def check_references(report, kjv):
    total, bad = 0, []
    for path in prose_files():
        text = read_prose(path)
        for m in REF_RE.finditer(text):
            book = BOOK_NAMES[m.group("book")]
            for chapter, verse in parse_list(book, m.group("list")):
                total += 1
                chapters = kjv[book]
                ok = 1 <= chapter <= len(chapters) and (verse is None or 1 <= verse <= len(chapters[chapter - 1]))
                if not ok:
                    line = text.count("\n", 0, m.start()) + 1
                    bad.append(f"{rel(path)}:{line} {m.group(0)}")
    bad = sorted(set(bad))
    report.add("FAIL" if bad else "PASS", "references-exist",
               f"{total} chapter and verse numbers checked; {len(bad)} point to no verse", bad)


def check_named_files(report):
    bad = []
    skill = read(os.path.join(SKILL, "SKILL.md"))
    sop_files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(SOPS, "*.md")))
    for name in sorted(set(re.findall(r"sops/([\w-]+\.md)", skill))):
        if name not in sop_files:
            bad.append(f"SKILL.md names sops/{name}, which does not exist")
    for label, path in (("README.md", os.path.join(ROOT, "README.md")), ("CLAUDE.md", os.path.join(ROOT, "CLAUDE.md"))):
        text = read(path)
        for name in sop_files:
            if name not in text:
                bad.append(f"{label} does not name sops/{name}")
        for name in sorted(set(re.findall(r"\b(\d\d-[\w-]+\.md)", text))):
            if name not in sop_files:
                bad.append(f"{label} names {name}, which does not exist")
    readme = read(os.path.join(ROOT, "README.md"))
    for path in sorted(glob.glob(os.path.join(ROOT, "skills", "*"))):
        name = os.path.basename(path)
        if name + "/" not in readme:
            bad.append(f"README.md does not list the skill folder {name}/")
    groups = [n for n in sop_files if re.match(r"1\d-", n)]
    overview = read(os.path.join(SOPS, "00-overview-and-template.md"))
    index_rows = re.findall(r"^\| (?!SOP name|---)([^|]+) \|", overview[overview.find("## Index of groups"):], flags=re.M)
    if len(index_rows) != len(groups):
        bad.append(f"the overview's index lists {len(index_rows)} SOPs, but there are {len(groups)} group files")
    bank = read_split("20-response-bank")
    plans = read_split("21-training-plans")
    for sop in (r.strip() for r in index_rows):
        short = re.sub(r"^The ", "", sop)
        if not re.search(r"^## .*" + re.escape(short), bank, flags=re.M):
            bad.append(f"the response bank has no table for {sop}")
        if not re.search(r"^## Training plan: .*" + re.escape(short), plans, flags=re.M):
            bad.append(f"the training plans have no plan for {sop}")
    report.add("FAIL" if bad else "PASS", "named-files",
               f"{len(sop_files)} SOP files, {len(index_rows)} groups in the index; {len(bad)} things out of step", bad)


def sections(text, heading_re):
    """Map each matching level-two heading to the text under it."""
    out, matches = {}, list(re.finditer(r"^## (.+)$", text, flags=re.M))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        found = re.match(heading_re, m.group(1))
        if found:
            out[found.group(1).strip()] = text[m.end():end]
    return out


def check_rows_and_personas(report):
    bank = read_split("20-response-bank")
    plans = read_split("21-training-plans")
    bank_tables = sections(bank, r"(?:The )?(.+?):")
    plan_tables = sections(plans, r"Training plan: (?:The )?(.+)")
    personas = {}
    for sop, persona in re.findall(r"^\| ([^|]+?) \| ([^|]+?) \| [^|]+ \|$", bank[:bank.find("**Rules for the role-player**")], flags=re.M):
        if sop not in ("SOP", "---"):
            personas.setdefault(sop.strip(), []).append(re.sub(r"\s*\([^()]*\)", "", persona).strip())
    bad, inspect, checked = [], [], 0
    for sop, plan in plan_tables.items():
        table = bank_tables.get(sop)
        if table is None:
            bad.append(f"{sop}: no table in the response bank")
            continue
        rows = {int(n) for n in re.findall(r"^\| (\d+) \|", table, flags=re.M)}
        known = personas.get(sop, [])
        plan_rows = [l for l in plan.splitlines() if re.match(r"\| \d+\. ", l)]
        for line in plan_rows:
            cells = [c.strip() for c in line.strip("|").split("|")]
            stage = cells[0]
            for cell in cells[2:4]:
                if "row" not in cell:
                    continue
                tail = REF_RE.sub(" ", cell[cell.find("row"):])  # "Isaiah 53" is not a row
                tail = re.sub(r"\d{1,3}(?:,\d{3})+", " ", tail)
                tail = re.sub(r"\([^()]*\)", lambda m: m.group(0) if "row" in m.group(0) else " ", tail)
                for n in (int(x) for x in re.findall(r"(?<![\w.:-])\d+(?![\w:-])", tail)):
                    if n >= 1000:
                        continue
                    checked += 1
                    if n not in rows:
                        bad.append(f"{sop}, stage {stage}: row {n} is not in the response bank")
            opponent = re.sub(r"\([^()]*\)", " ", cells[3])
            opponent = re.sub(r";?\s*(?:bank )?rows?\b.*", "", opponent)
            for phrase in re.split(r";|,\s*then\s+|,", opponent):
                phrase = re.sub(r"^(?:then\s+)?(?:an?\s+)?", "", phrase.strip(), flags=re.I)
                phrase = re.sub(r"\s+steamrolling$", "", phrase)
                if not phrase or phrase in ("None", "Any persona"):
                    continue
                if phrase.lower() not in (k.lower() for k in known):
                    inspect.append(f"{sop}, stage {stage}: opponent \"{phrase}\" is not a persona in the response bank")
        for persona in known:
            if persona.lower() not in plan.lower():
                inspect.append(f"{sop}: the persona \"{persona}\" is never used in its training plan")
    report.add("FAIL" if bad else "PASS", "bank-rows",
               f"{checked} row numbers in the training plans checked against the response bank; {len(bad)} missing", bad)
    if inspect:
        report.add("INSPECT", "personas", "opponents the response bank does not define, or personas never used", inspect)


def check_saved_skills(report, saved_dir):
    if saved_dir is None:
        found = glob.glob(os.path.expanduser("~/.claude/skills/synced/*/apologetics-boot-camp"))
        saved_dir = os.path.dirname(found[0]) if found else None
    if not saved_dir or not os.path.isdir(saved_dir):
        report.add("SKIP", "saved-skills", "no saved copies of the skills on this machine")
        return
    bad, notes, same = [], [], 0
    for path in sorted(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md"))):
        name = os.path.basename(os.path.dirname(path))
        saved = os.path.join(saved_dir, name, "SKILL.md")
        if not os.path.exists(saved):
            notes.append(f"{name}: no saved copy")
            continue
        ours, theirs = read(path), read(saved)
        if body_of(ours).strip() == body_of(theirs).strip():
            same += 1
        else:
            bad.append(f"{name}: the saved copy differs from GitHub")
    report.add("FAIL" if bad else "PASS", "saved-skills",
               f"{same} saved skills match GitHub; {len(bad)} differ", bad)
    if notes:
        report.add("INSPECT", "saved-skills", "skills in the repo with no saved copy here", notes)


# The stamp lets a saved copy of the skill tell, from one short line on GitHub,
# whether it is still current, without fetching the whole of SKILL.md again.
STAMP_RE = re.compile(r"(This copy's stamp is `)([0-9a-f]{8})(`)")
VERSION_FILE = os.path.join(SKILL, "VERSION")


def stamp_of(text):
    """The stamp a SKILL.md should carry: the first eight hex digits of the
    SHA-256 of its body, read with the stamp itself set to zeros."""
    body = STAMP_RE.sub(lambda m: m.group(1) + "0" * 8 + m.group(3), body_of(text)).strip()
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:8]


def write_stamp():
    """Set the stamp in SKILL.md and in VERSION to match the skill's text."""
    path = os.path.join(SKILL, "SKILL.md")
    text = read(path)
    want = stamp_of(text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(STAMP_RE.sub(lambda m: m.group(1) + want + m.group(3), text))
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(want + "\n")
    return want


def check_stamp(report):
    text = read(os.path.join(SKILL, "SKILL.md"))
    want, found, bad = stamp_of(text), STAMP_RE.search(text), []
    if not found:
        bad.append("SKILL.md carries no stamp")
    elif found.group(2) != want:
        bad.append(f"SKILL.md carries the stamp {found.group(2)}, but its text now gives {want}")
    if not os.path.exists(VERSION_FILE):
        bad.append("skills/apologetics-boot-camp/VERSION is missing")
    elif read(VERSION_FILE).strip() != want:
        bad.append(f"VERSION holds {read(VERSION_FILE).strip()}, but the skill's text gives {want}")
    detail = (f"the stamp {want} is in SKILL.md and in VERSION" if not bad
              else "the stamp is out of date; run python3 measure/checks.py --stamp")
    report.add("FAIL" if bad else "PASS", "skill-stamp", detail, bad)


def check_fixed(report):
    """The fixed pieces, against the layout in fixed/README.md (fixed_pieces.py)."""
    import fixed_pieces
    stamp = read(VERSION_FILE).strip() if os.path.exists(VERSION_FILE) else ""
    total, errors, notes = 0, [], []
    paths = [p for p in sorted(glob.glob(os.path.join(FIXED, "*.md")))
             if os.path.basename(p) not in ("README.md", "TO-CHECK.md")]
    for path in paths:
        count, errs, nts = fixed_pieces.check_file(path, stamp)
        total += count
        errors += [f"{os.path.basename(path)}: {e}" for e in errs]
        notes += [f"{os.path.basename(path)}: {n}" for n in nts]
    report.add("FAIL" if errors else "PASS", "fixed-pieces",
               f"{len(paths)} files, {total} pieces; {len(errors)} could not be used", errors)
    if notes:
        report.add("INSPECT", "fixed-pieces", "written from an older copy of the skill", notes)


def check_length(report):
    lines = read(os.path.join(SKILL, "SKILL.md")).count("\n")
    report.add("FAIL" if lines > 500 else "PASS", "skill-length",
               f"SKILL.md is {lines} lines; the limit is 500")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--saved", help="folder holding the saved copies of the skills")
    parser.add_argument("--kjv", help="a local copy of the King James text (same file as the fixed version)")
    parser.add_argument("--stamp", action="store_true",
                        help="first set the stamp in SKILL.md and in VERSION to match the skill's text")
    args = parser.parse_args()
    if args.stamp:
        write_stamp()

    report = Report()
    try:
        kjv = load_kjv(args.kjv)
    except Exception as err:  # no text, no verdict: say so plainly
        report.add("FAIL", "kjv-text", f"could not load the King James text: {err}")
        kjv = None
    if kjv:
        check_quotations(report, kjv)
        check_references(report, kjv)
    check_named_files(report)
    check_rows_and_personas(report)
    check_saved_skills(report, args.saved)
    check_stamp(report)
    check_fixed(report)
    check_length(report)

    if args.json:
        print(json.dumps(report.rows, indent=2, ensure_ascii=False))
    else:
        report.print()
    return 1 if report.failed() else 0


if __name__ == "__main__":
    sys.exit(main())
