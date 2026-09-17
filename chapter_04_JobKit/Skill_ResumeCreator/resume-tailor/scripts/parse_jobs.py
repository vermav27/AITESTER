#!/usr/bin/env python3
"""
Parse job descriptions from a spreadsheet or text file into jobs.json.

Usage:
    python parse_jobs.py <file.xlsx|.xlsm|.csv|.tsv|.txt|.md> [-o jobs.json]

Supported layouts:
  1. Table layout (recommended, matches assets/job_descriptions_template.xlsx):
     a header row (anywhere in the first 15 rows) and one job per row.
     Headers are matched loosely, e.g. "Must-Have Skills", "Required", "Requirements".
  2. List layout: a sheet with no recognizable header row is treated as ONE job.
     Title = sheet name. Lines like "Company: X" / "Title: Y" are picked up;
     all other non-empty cells become requirement items.
  3. Plain text (.txt/.md): the whole file is one job, stored in full_text.

Rows whose Job ID starts with "EXAMPLE" are skipped, as are sheets named
Instructions / How to use / Legend / README.

List cells are split on new lines, semicolons, and bullet characters.
Short comma-separated cells ("Java, SQL, Jira") are split on commas too.

Output shape:
{
  "source": "<file>",
  "jobs": [
    {"id": "JOB-1", "company": "", "title": "", "location": "",
     "must_have": [], "nice_to_have": [], "responsibilities": [],
     "keywords": [], "missing_keywords": [], "full_text": "",
     "link": "", "notes": "", "sheet": "", "row": 2}
  ],
  "skipped": ["reasons..."]
}
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

LIST_FIELDS = ["must_have", "nice_to_have", "responsibilities", "keywords", "missing_keywords"]
TEXT_FIELDS = ["id", "company", "title", "location", "full_text", "link", "notes"]

# Order matters: more specific synonyms first (checked by longest match).
HEADER_SYNONYMS = {
    "id": ["job id", "id", "#", "s no", "sno", "sr no", "serial", "no"],
    "company": ["company", "employer", "organization", "organisation", "client", "company name"],
    "title": ["job title", "title", "role", "position", "designation", "job role"],
    "location": ["location", "work hours", "hours", "shift", "location work hours", "location hours", "work location"],
    "must_have": ["must have skills", "must have", "must haves", "required skills", "requirements", "required",
                  "mandatory skills", "mandatory", "essential skills", "essential", "qualifications",
                  "required qualifications", "skills and abilities"],
    "nice_to_have": ["nice to have skills", "nice to have", "nice to haves", "preferred skills", "preferred",
                     "good to have", "bonus", "optional", "desirable", "preferred qualifications"],
    "responsibilities": ["responsibilities", "key responsibilities", "duties", "essential duties",
                         "duties and responsibilities", "what you will do", "role summary", "job summary"],
    "missing_keywords": ["missing keywords from ats scan", "missing keywords", "missing", "ats missing keywords",
                         "keywords missing", "gaps", "missing skills"],
    "keywords": ["keywords", "key skills", "skills", "tech stack", "technologies", "tools"],
    "full_text": ["full job description", "full job description optional", "job description", "jd", "full jd",
                  "description", "full text", "jd text"],
    "link": ["job link", "link", "url", "posting url", "job url"],
    "notes": ["notes", "comments", "remarks"],
}
SKIP_SHEETS = {"instructions", "how to use", "legend", "readme", "read me", "guide"}
BULLET_RE = re.compile(r"^\s*(?:[-*•▪◦●‣]|\d+[.)])\s*")


def norm(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9#]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def match_header(cell):
    """Return the field name for a header cell, or None."""
    h = norm(cell)
    if not h:
        return None
    best, best_len = None, 0
    for field, syns in HEADER_SYNONYMS.items():
        for s in syns:
            if h == s or (len(s) > 3 and (h.startswith(s + " ") or h.endswith(" " + s))):
                if len(s) > best_len:
                    best, best_len = field, len(s)
    return best


def split_items(value):
    if value is None:
        return []
    text = str(value).replace("\r", "\n").strip()
    if not text:
        return []
    parts = re.split(r"\n|;|(?<=\S)\s*[•▪●]\s*", text)
    items = []
    for p in parts:
        p = BULLET_RE.sub("", p).strip(" \t,")
        if p:
            items.append(p)
    # Short comma lists in a single line: "Java, SQL, Jira"
    if len(items) == 1 and "," in items[0]:
        chunks = [c.strip() for c in items[0].split(",") if c.strip()]
        avg = sum(len(c) for c in chunks) / max(len(chunks), 1)
        if (len(chunks) >= 3 and avg < 40) or (len(chunks) == 2 and avg < 25):
            items = chunks
    return items


def empty_job():
    job = {f: "" for f in TEXT_FIELDS}
    job.update({f: [] for f in LIST_FIELDS})
    job.update({"sheet": "", "row": None})
    return job


def rows_to_jobs(rows, sheet_name, skipped):
    """rows: list of lists of cell values."""
    header_idx, mapping = None, {}
    for i, row in enumerate(rows[:15]):
        m = {}
        for j, cell in enumerate(row):
            field = match_header(cell)
            if field and field not in m.values():
                m[j] = field
        if len(m) >= 2:
            header_idx, mapping = i, m
            break

    jobs = []
    if header_idx is not None:
        for r, row in enumerate(rows[header_idx + 1:], start=header_idx + 2):
            if not any(str(c or "").strip() for c in row):
                continue
            job = empty_job()
            job["sheet"], job["row"] = sheet_name, r
            for j, field in mapping.items():
                val = row[j] if j < len(row) else None
                if field in LIST_FIELDS:
                    job[field] = split_items(val)
                else:
                    job[field] = str(val).strip() if val is not None else ""
            if job["id"].upper().startswith("EXAMPLE"):
                skipped.append(f"{sheet_name} row {r}: example row skipped")
                continue
            if not (job["company"] or job["title"] or job["full_text"] or job["must_have"]):
                skipped.append(f"{sheet_name} row {r}: no company/title/requirements, skipped")
                continue
            jobs.append(job)
        return jobs

    # List layout: whole sheet is one job
    job = empty_job()
    job["sheet"], job["title"] = sheet_name, sheet_name
    items, lines = [], []
    for row in rows:
        for cell in row:
            text = str(cell or "").strip()
            if not text:
                continue
            lines.append(text)
            kv = re.match(r"^\s*([A-Za-z /\-]+?)\s*:\s*(.+)$", text)
            field = match_header(kv.group(1)) if kv else None
            if field in TEXT_FIELDS:
                job[field] = kv.group(2).strip()
            elif field in LIST_FIELDS:
                job[field].extend(split_items(kv.group(2)))
            else:
                items.extend(split_items(text))
    if not lines:
        return []
    job["must_have"].extend(items)
    job["full_text"] = job["full_text"] or "\n".join(lines)
    return [job]


def read_xlsx(path, skipped):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    jobs = []
    for ws in wb.worksheets:
        if norm(ws.title) in SKIP_SHEETS:
            continue
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        jobs.extend(rows_to_jobs(rows, ws.title, skipped))
    return jobs


def read_csv(path, skipped, delimiter=None):
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(text[:4096], delimiters=",\t;").delimiter
        except csv.Error:
            delimiter = ","
    rows = list(csv.reader(text.splitlines(), delimiter=delimiter))
    return rows_to_jobs(rows, Path(path).stem, skipped)


def read_text(path):
    job = empty_job()
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    job["title"] = Path(path).stem
    job["full_text"] = text
    return [job]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("-o", "--output", default="jobs.json")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        sys.exit(f"File not found: {path}")
    skipped = []
    ext = path.suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        jobs = read_xlsx(path, skipped)
    elif ext == ".csv":
        jobs = read_csv(path, skipped)
    elif ext == ".tsv":
        jobs = read_csv(path, skipped, delimiter="\t")
    elif ext in (".txt", ".md"):
        jobs = read_text(path)
    elif ext == ".xls":
        sys.exit("Legacy .xls: convert first, e.g. soffice --headless --convert-to xlsx file.xls")
    else:
        sys.exit(f"Unsupported file type: {ext}")

    for n, job in enumerate(jobs, start=1):
        base = job["id"] or f"JOB-{n}"
        job["id"] = re.sub(r"[^A-Za-z0-9_-]+", "-", base).strip("-") or f"JOB-{n}"

    out = {"source": str(path), "jobs": jobs, "skipped": skipped}
    Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Detected {len(jobs)} job(s) from {path.name} -> {args.output}")
    for job in jobs:
        counts = ", ".join(f"{f}={len(job[f])}" for f in LIST_FIELDS if job[f])
        extra = " +full_text" if job["full_text"] else ""
        print(f"  [{job['id']}] {job['company'] or '?'} - {job['title'] or '?'}  ({counts or 'no lists'}{extra})")
    for s in skipped:
        print(f"  note: {s}")


if __name__ == "__main__":
    main()
