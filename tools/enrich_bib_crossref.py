#!/usr/bin/env python3
"""Add verified DOI links to a BibTeX bibliography using Crossref metadata.

Uses title/author matching and only applies high-confidence matches. Existing DOI
and html fields are preserved. A JSON report is always written for audit.
"""
from __future__ import annotations

import argparse, difflib, json, re, ssl, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BIB = ROOT / "_bibliography" / "papers.bib"


def normalise(value: str) -> str:
    value = re.sub(r"[{}\\]", "", value.lower())
    value = re.sub(r"\b(the|a|an)\b", " ", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def entries(text: str):
    cursor = 0
    pattern = re.compile(r"@(article|inproceedings|misc|book|incollection)\s*\{\s*([^,]+),", re.I)
    while match := pattern.search(text, cursor):
        depth, pos = 1, match.end()
        while pos < len(text) and depth:
            if text[pos] == "{": depth += 1
            elif text[pos] == "}": depth -= 1
            pos += 1
        yield match.group(2), match.start(), pos, text[match.start():pos]
        cursor = pos


def field(record: str, key: str) -> str:
    match = re.search(rf"(?mi)^\s*{re.escape(key)}\s*=\s*\{{(.+?)\}}\s*,?\s*$", record)
    return match.group(1).strip() if match else ""


def crossref(title: str):
    params = urllib.parse.urlencode({"query.title": title, "rows": 5, "select": "DOI,title,author,container-title,type,URL"})
    request = urllib.request.Request(
        "https://api.crossref.org/works?" + params,
        headers={"User-Agent": "WQPu.github.io bibliography maintainer (mailto:wenqiangpu@cuhk.edu.cn)"},
    )
    with urllib.request.urlopen(request, timeout=25, context=ssl._create_unverified_context()) as response:
        return json.load(response)["message"]["items"]


def score(local_title: str, local_author: str, candidate: dict) -> float:
    candidate_title = " ".join(candidate.get("title", []))
    title_score = difflib.SequenceMatcher(None, normalise(local_title), normalise(candidate_title)).ratio()
    first_local = normalise(local_author.split(" and ")[0]).split()
    first = candidate.get("author", [{}])[0] if candidate.get("author") else {}
    first_crossref = normalise(f"{first.get('given', '')} {first.get('family', '')}").split()
    author_bonus = 0.04 if first_local and first_crossref and first_local[-1] == first_crossref[-1] else 0
    return min(1.0, title_score + author_bonus)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bib", type=Path, default=DEFAULT_BIB)
    parser.add_argument("--apply", action="store_true", help="write high-confidence DOI fields into the BibTeX file")
    parser.add_argument("--min-score", type=float, default=0.91)
    parser.add_argument("--sleep", type=float, default=0.12)
    args = parser.parse_args()

    text = args.bib.read_text(encoding="utf-8")
    report, replacements = [], []
    for key, start, end, record in entries(text):
        title, author = field(record, "title"), field(record, "author")
        existing = field(record, "doi")
        if not title or existing:
            continue
        try:
            candidates = crossref(title)
            best = max(candidates, key=lambda item: score(title, author, item), default={})
            confidence = score(title, author, best) if best else 0
            doi = best.get("DOI", "")
            accepted = bool(doi and confidence >= args.min_score)
            report.append({"key": key, "title": title, "doi": doi, "score": round(confidence, 3), "accepted": accepted, "candidate_title": " ".join(best.get("title", []))})
            if accepted:
                insertion = f"  doi = {{{doi}}},\n"
                replacements.append((start, end, record.rstrip()[:-1] + ",\n" + insertion + "}\n"))
        except Exception as exc:
            report.append({"key": key, "title": title, "error": str(exc), "accepted": False})
        time.sleep(args.sleep)

    report_path = args.bib.with_suffix(".crossref-report.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.apply and replacements:
        for start, end, replacement in reversed(replacements):
            text = text[:start] + replacement + text[end:]
        args.bib.write_text(text, encoding="utf-8")
    print(f"Checked {len(report)} records; accepted {sum(x.get('accepted', False) for x in report)} DOI matches. Report: {report_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
