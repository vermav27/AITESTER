#!/usr/bin/env python3
"""
Rough keyword coverage check: which job-description terms appear in a resume?

Usage:
    python keyword_coverage.py jobs.json resume.(txt|html) [--job JOB-1] [--json out.json]

How terms are built for each job:
  - Every item from must_have, nice_to_have, keywords, and missing_keywords.
  - Long sentence items are broken into short phrases: filler such as
    "experience with" or "strong understanding of" is removed, and the rest is
    split on commas, slashes-with-spaces, parentheses, "and", and "or".
  - If the job only has full_text, the most frequent meaningful one- and
    two-word phrases (appearing 2+ times) are used.

Matching is case-insensitive on normalized text ("UI/UX" matches "ui ux").
A trailing "s" is optional. This is a string matcher, not an ATS: use your
judgment for synonyms (e.g. "defect tracking" vs "bug tracking").
"""
import argparse
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

FILLER = [
    r"\d+\+?\s*years? of", r"experience (?:with|in|working with|working in)", r"strong (?:understanding|knowledge|experience) (?:of|with|in)",
    r"strong", r"solid", r"proven", r"hands[- ]on", r"familiarity with", r"familiar with", r"knowledge of", r"understanding of",
    r"ability to", r"proficiency (?:in|with)", r"proficient (?:in|with)", r"working knowledge of", r"exposure to",
    r"expertise in", r"background in", r"skills? in", r"or similar", r"e\.?g\.?", r"etc\.?", r"including", r"such as",
    r"main", r"level", r"other", r"various", r"multiple",
]
STOP = set("""a an the and or of for to in on with at by from as is are be this that these those we you our your
will can may must should across both into their its it all any each other more most such than then also very
using use used work working role position job candidate ensure ensuring including within well
new existing strong experience years year ability etc""".split())


def normalize(text):
    text = html.unescape(text).lower()
    text = re.sub(r"[^a-z0-9+#]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return " " + text + " "


def strip_html(text):
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(text)


def phrases_from_item(item):
    low = " " + item.strip().lower() + " "
    for f in FILLER:
        low = re.sub(rf"\b{f}\b", " ", low)
    # Split "Scrum/Kanban" but keep short pairs like "UI/UX" and "CI/CD" together
    low = re.sub(r"\b([a-z0-9+#]{4,})\s*/\s*([a-z0-9+#]{4,})\b", r"\1 , \2", low)
    splitter = r",|;|\(|\)|\s/\s|:"
    if len(low.split()) > 4:
        splitter += r"|\band\b|\bor\b"
    out = []
    for c in re.split(splitter, low):
        words = re.sub(r"\s+", " ", c).strip(" .-").split()
        while words and words[0] in STOP:
            words.pop(0)
        while words and words[-1] in STOP:
            words.pop()
        if words and len(words) <= 5:
            out.append(" ".join(words))
    return out


def frequent_terms(text, min_count=2, limit=40):
    words = [w for w in normalize(text).split() if w not in STOP and len(w) > 1 and not w.isdigit()]
    uni = Counter(words)
    bi = Counter(f"{a} {b}" for a, b in zip(words, words[1:]))
    terms = [t for t, c in bi.most_common() if c >= min_count][:limit // 2]
    covered_words = {w for t in terms for w in t.split()}
    terms += [t for t, c in uni.most_common() if c >= min_count and t not in covered_words][:limit - len(terms)]
    return terms


def term_in(term, resume_norm):
    n = normalize(term).strip()
    if not n:
        return True
    pattern = r"\s" + r"\s".join(re.escape(w) + (r"s?" if w[-1].isalpha() else "") for w in n.split()) + r"\s"
    if re.search(pattern, resume_norm):
        return True
    if n.endswith("s") and len(n) > 3:  # plural term vs singular resume text
        return f" {n[:-1]} " in resume_norm
    return False


def job_terms(job):
    seen, terms = set(), []
    for field in ["must_have", "nice_to_have", "keywords", "missing_keywords"]:
        for item in job.get(field, []):
            for p in phrases_from_item(item):
                key = normalize(p).strip()
                if key and key not in seen:
                    seen.add(key)
                    terms.append((p, field))
    if not terms and job.get("full_text"):
        terms = [(t, "full_text") for t in frequent_terms(job["full_text"])]
    return terms


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jobs")
    ap.add_argument("resume")
    ap.add_argument("--job", help="Job id to check (default: all)")
    ap.add_argument("--json", help="Write detailed results to this JSON file")
    args = ap.parse_args()

    jobs = json.loads(Path(args.jobs).read_text(encoding="utf-8"))["jobs"]
    if args.job:
        jobs = [j for j in jobs if j["id"] == args.job]
        if not jobs:
            sys.exit(f"No job with id {args.job}")
    raw = Path(args.resume).read_text(encoding="utf-8", errors="replace")
    if args.resume.lower().endswith((".html", ".htm")) or "<body" in raw.lower():
        raw = strip_html(raw)
    resume_norm = normalize(raw)

    results = []
    for job in jobs:
        terms = job_terms(job)
        covered = [(t, f) for t, f in terms if term_in(t, resume_norm)]
        missing = [(t, f) for t, f in terms if not term_in(t, resume_norm)]
        pct = round(100 * len(covered) / len(terms)) if terms else 0
        results.append({"id": job["id"], "company": job.get("company", ""), "title": job.get("title", ""),
                        "coverage_pct": pct, "covered": [t for t, _ in covered],
                        "missing": [{"term": t, "source": f} for t, f in missing]})
        print(f"\n[{job['id']}] {job.get('company') or '?'} - {job.get('title') or '?'}: "
              f"{len(covered)}/{len(terms)} terms covered ({pct}%)")
        if missing:
            print("  Missing:")
            for t, f in missing:
                print(f"    - {t}   ({f})")
        if covered:
            print("  Covered: " + ", ".join(t for t, _ in covered))

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
