#!/usr/bin/env python3
"""
Lint a piece of Vineet's content pack against his brand rules.

Usage:
    python scripts/lint_content.py linkedin post.txt
    python scripts/lint_content.py medium article.md
    python scripts/lint_content.py card card_prompt.txt
    cat post.txt | python scripts/lint_content.py linkedin -

Prints PASS / WARN / FAIL lines. Exit code is 1 if any FAIL, otherwise 0.
Standard library only.
"""

import re
import sys

BANNED = [
    "thrilled to share",
    "delighted to share",
    "game-changer",
    "game changer",
    "fast-paced world",
    "leverage",
    "unlock",
    "delve",
    "seamless",
    "journey",
    "agree?",
    "real answers only",
    "real numbers only",
    "rules, not vibes",
    "hope with a green checkmark",
    "qa is dead",
    "nobody talks about this",
    "qa is getting a package manager",
]

EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"  # symbols, pictographs, emoticons, transport, etc.
    "\U0001F000-\U0001F2FF"  # mahjong, dominoes, playing cards, enclosed chars
    "\U00002600-\U000026FF"  # misc symbols
    "\U00002700-\U000027BF"  # dingbats
    "\U0000FE0F"             # variation selector
    "]"
)
BOLD_UNICODE_RE = re.compile("[\U0001D400-\U0001D7FF]")
URL_RE = re.compile(r"https?://|www\.", re.I)
# Rough detector for "X isn't Y. It's Z." style constructions.
NOT_X_ITS_Y_RE = re.compile(
    r"\b(isn't|is not|wasn't|was not|aren't|are not|doesn't|does not)\b[^.!?\n]*[.!?]\s+"
    r"(it's|it is|it was|that's|that is|they're|they are)\b",
    re.I,
)

results = []


def report(level, msg):
    results.append((level, msg))


def words(text):
    return [w for w in re.split(r"\s+", text.strip()) if w]


def strip_code_blocks(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def check_common(text, not_x_limit):
    lower = text.lower()
    hits = [b for b in BANNED if b in lower]
    if hits:
        for b in hits:
            report("FAIL", f'Banned phrase: "{b}"')
    else:
        report("PASS", "No banned phrases")

    emojis = EMOJI_RE.findall(text)
    if emojis:
        report("FAIL", f"Emojis found: {''.join(sorted(set(emojis)))}")
    else:
        report("PASS", "No emojis")

    if BOLD_UNICODE_RE.search(text):
        report("FAIL", "Bold/italic unicode letters found")

    n = len(NOT_X_ITS_Y_RE.findall(text))
    if n > not_x_limit:
        report("WARN", f"Possible \"isn't X, it's Y\" lines: {n} (limit {not_x_limit})")
    else:
        report("PASS", f"\"isn't X, it's Y\" lines: {n} (limit {not_x_limit})")


def lint_linkedin(text):
    text = text.strip("\n")
    lines = text.split("\n")
    non_empty = [l for l in lines if l.strip()]

    # Hashtags on the last line; body = everything else
    last = non_empty[-1] if non_empty else ""
    last_tags = re.findall(r"#\w+", last)
    tag_line_only = bool(last_tags) and all(w.startswith("#") for w in words(last))
    body = "\n".join(lines[:-1]) if tag_line_only else text
    if tag_line_only and lines[-1].strip() != last.strip():
        body = text.replace(last, "")

    wc = len([w for w in words(body) if not w.startswith("#")])
    if wc < 120 or wc > 350:
        report("FAIL", f"Word count {wc} (target 150-300)")
    elif wc < 150 or wc > 300:
        report("WARN", f"Word count {wc} (target 150-300)")
    else:
        report("PASS", f"Word count {wc}")

    first = non_empty[0] if non_empty else ""
    fw = len(words(first))
    report("PASS" if fw <= 15 else "WARN", f"Hook line 1: {fw} words (max 15)")

    if tag_line_only and 3 <= len(last_tags) <= 5:
        report("PASS", f"{len(last_tags)} hashtags on the last line")
    else:
        report("WARN", f"Hashtags on last line: {len(last_tags) if tag_line_only else 0} (want 3-5, alone on the last line)")
    if tag_line_only and "#qa" not in [t.lower() for t in last_tags]:
        report("WARN", "#QA missing from hashtags")
    if re.search(r"#\w+", body):
        report("WARN", "Hashtag inside the body")

    if URL_RE.search(body):
        report("WARN", "Link in the body (links go in the first comment)")
    if "**" in body or "__" in body:
        report("WARN", "Markdown bold in the body (LinkedIn shows it as asterisks)")

    arrows = [l for l in lines if l.strip().startswith("→")]
    report("PASS" if arrows else "WARN", f"Arrow steps: {len(arrows)}")
    if len(arrows) > 7:
        report("WARN", "More than 7 arrows; group them and move the full list to Medium")

    ps = [l for l in lines if l.strip().startswith("PS")]
    if not ps:
        report("WARN", "No PS line")
    elif "no judgment here" not in ps[-1].lower():
        report("WARN", 'PS does not end with "so no judgment here"')
    else:
        report("PASS", "PS sign-off present")

    for para in re.split(r"\n\s*\n", body):
        p = para.strip()
        if not p or p.startswith("→") or p.startswith("○"):
            continue
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]
        if len(sentences) > 2:
            report("WARN", f'Paragraph with {len(sentences)} sentences: "{p[:50]}..."')

    check_common(body, not_x_limit=1)


def lint_medium(text):
    prose = strip_code_blocks(text)
    wc = len(words(prose))
    if wc < 800 or wc > 2200:
        report("FAIL", f"Word count {wc} excluding code (target 1,000-1,800)")
    elif wc < 1000 or wc > 1800:
        report("WARN", f"Word count {wc} excluding code (target 1,000-1,800)")
    else:
        report("PASS", f"Word count {wc} excluding code")

    heads = re.findall(r"^#{2,3} .+$", prose, flags=re.M)
    report("PASS" if 3 <= len(heads) <= 6 else "WARN", f"Section headings: {len(heads)} (want 3-6)")

    checks = [
        ("```" in text, "Code block"),
        (re.search(r"^\|.+\|\s*$", prose, flags=re.M) is not None, "Table"),
        (re.search(r"^\s*[-*] ", prose, flags=re.M) is not None, "Bullet list"),
        (re.search(r"^> ", prose, flags=re.M) is not None, "Pull quote"),
        ("what i'd do if i started tomorrow" in prose.lower(), '"What I\'d do if I started tomorrow" section'),
        ("no judgment here" in prose.lower(), '"so no judgment here" offer line'),
        ("vineet verma" in prose.lower(), "Bio"),
    ]
    for ok, label in checks:
        report("PASS" if ok else "WARN", f"{label}: {'present' if ok else 'missing'}")

    if re.search(r"waitForTimeout|sleep\(", text):
        report("FAIL", "Hard wait in code (use web-first assertions)")

    check_common(prose, not_x_limit=3)


def lint_card(text):
    lines = text.split("\n")
    start = end = None
    for i, l in enumerate(lines):
        if start is None and "with nothing added" in l.lower():
            start = i + 1
        elif start is not None and l.strip().lower().startswith("color only"):
            end = i
            break
    card = "\n".join(lines[start:end]) if start is not None and end is not None else text

    blocks = [b.strip() for b in re.split(r"\n\s*\n", card) if b.strip()]
    total = sum(len(words(b)) for b in blocks)
    report("PASS" if total <= 30 else "WARN", f"Card text: {total} words in {len(blocks)} blocks (max 30)")
    report("PASS" if len(blocks) == 3 else "WARN", f"Blocks: {len(blocks)} (want 3)")
    for b in blocks:
        if len(words(b)) > 12:
            report("WARN", f'Long block ({len(words(b))} words): "{b[:40]}..."')
    risky = sorted(set(re.findall(r"[→–—/&…]", card)))
    if risky:
        report("WARN", f"Symbols image models often garble: {' '.join(risky)}")
    if re.search(r"#\w+", card):
        report("FAIL", "Hashtag in card text")
    if EMOJI_RE.search(card):
        report("FAIL", "Emoji in card text")

    lower = text.lower()
    report("PASS" if "#f4212e" in lower else "WARN", f"Red threat highlight: {'present' if '#f4212e' in lower else 'missing'}")
    report("PASS" if "#00ba7c" in lower else "WARN", f"Green way-out highlight: {'present' if '#00ba7c' in lower else 'missing'}")
    report("PASS" if "attached headshot" in lower else "WARN", "Headshot instruction")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in {"linkedin", "medium", "card"}:
        print(__doc__)
        sys.exit(2)
    mode, path = sys.argv[1], sys.argv[2]
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()

    {"linkedin": lint_linkedin, "medium": lint_medium, "card": lint_card}[mode](text)

    for level, msg in results:
        print(f"{level:4}  {msg}")
    fails = sum(1 for l, _ in results if l == "FAIL")
    warns = sum(1 for l, _ in results if l == "WARN")
    print(f"\n{fails} fail, {warns} warn")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
