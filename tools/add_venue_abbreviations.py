#!/usr/bin/env python3
"""Add concise venue labels to Google Scholar-exported BibTeX entries."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIB = ROOT / "_bibliography" / "papers.bib"


def venue_label(value: str) -> str | None:
    v = value.lower()
    rules = [
        ("transactions on signal processing", "IEEE TSP"),
        ("transactions on aerospace and electronic systems", "IEEE TAES"),
        ("transactions on wireless communications", "IEEE TWC"),
        ("transactions on mobile computing", "IEEE TMC"),
        ("transactions on geoscience and remote sensing", "IEEE TGRS"),
        ("transactions on vehicular technology", "IEEE TVT"),
        ("signal processing letters", "IEEE SPL"),
        ("sensors journal", "IEEE Sens. J."),
        ("systems journal", "IEEE Syst. J."),
        ("information fusion", "Inf. Fusion"),
        ("mathematical programming", "Math. Program."),
        ("remote sensing", "Remote Sens."),
        ("signal processing", "Signal Process."),
        ("international conference on acoustics", "ICASSP"),
        ("wireless communications and networking conference", "WCNC"),
        ("sensor array and multichannel signal processing", "SAM"),
        ("signal processing advances in wireless communications", "SPAWC"),
        ("international radar conference", "IEEE Radar"),
        ("conference on radar", "Radar"),
        ("global conference on signal and information processing", "GlobalSIP"),
        ("asilomar", "Asilomar"),
        ("european signal processing conference", "EUSIPCO"),
        ("chinese control conference", "CCC"),
        ("machine learning", "ICML"),
        ("arxiv", "arXiv"),
    ]
    for needle, label in rules:
        if needle in v:
            return label
    return None


def main() -> int:
    text = BIB.read_text(encoding="utf-8")
    pattern = re.compile(r"@(article|inproceedings|misc|book|incollection)\s*\{\s*[^,]+,", re.I)
    out, cursor, added = [], 0, 0
    while match := pattern.search(text, cursor):
        out.append(text[cursor:match.start()])
        depth, pos = 1, match.end()
        while pos < len(text) and depth:
            depth += (text[pos] == "{") - (text[pos] == "}")
            pos += 1
        record = text[match.start():pos]
        if not re.search(r"(?mi)^\s*abbr\s*=", record):
            venue_match = re.search(r"(?mi)^\s*(journal|booktitle)\s*=\s*\{(.+?)\}\s*,?\s*$", record)
            label = venue_label(venue_match.group(2)) if venue_match else None
            if label:
                record = record.rstrip()[:-1] + f"  abbr = {{{label}}},\n}}\n"
                added += 1
        out.append(record)
        cursor = pos
    out.append(text[cursor:])
    BIB.write_text("".join(out), encoding="utf-8")
    print(f"Added venue abbreviations to {added} records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
