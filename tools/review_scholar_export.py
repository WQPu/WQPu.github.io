#!/usr/bin/env python3
"""Compare a manually exported Google Scholar BibTeX file with papers.bib.

This tool intentionally does not scrape Google Scholar. Export publications from
Google Scholar (BibTeX), then run:

  python3 tools/review_scholar_export.py /path/to/scholar-export.bib

It prints likely new records plus title/year/author differences for review.
No bibliography data is overwritten automatically.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "_bibliography" / "papers.bib"


def norm(value: str) -> str:
    value = re.sub(r"[{}\\]", "", value.lower())
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def fields(text: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for chunk in re.split(r"(?=@\w+\s*\{)", text):
        if not chunk.lstrip().startswith("@"):
            continue
        item = {key.lower(): value.strip() for key, value in re.findall(r'(\w+)\s*=\s*[{"](.+?)[}"]\s*,?', chunk, flags=re.S)}
        if item.get("title"):
            records.append(item)
    return records


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 tools/review_scholar_export.py /path/to/scholar-export.bib")
        return 2

    export = Path(sys.argv[1])
    if not export.exists():
        print(f"Export not found: {export}")
        return 2

    local = fields(MASTER.read_text(encoding="utf-8"))
    scholar = fields(export.read_text(encoding="utf-8"))
    by_title = {norm(item["title"]): item for item in local}

    added = []
    differences = []
    for item in scholar:
        existing = by_title.get(norm(item["title"]))
        if not existing:
            added.append(item)
            continue
        changed = [key for key in ("author", "year", "journal", "booktitle") if item.get(key) and norm(item.get(key, "")) != norm(existing.get(key, ""))]
        if changed:
            differences.append((item, existing, changed))

    print(f"Scholar export: {len(scholar)} records | Site bibliography: {len(local)} records\n")
    print(f"Potentially new records ({len(added)}):")
    for item in added:
        print(f"- {item.get('year', 'n.d.')} — {item['title']}")

    print(f"\nRecords needing metadata review ({len(differences)}):")
    for scholar_item, local_item, changed in differences:
        print(f"- {scholar_item['title']}\n  fields: {', '.join(changed)}")
        for field in changed:
            print(f"  Scholar: {scholar_item.get(field, '')}\n  Site:    {local_item.get(field, '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
