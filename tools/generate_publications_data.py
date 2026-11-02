#!/usr/bin/env python3
"""Generate publication indexes from BibTeX and structured annotations.

Use local PubPaperPDFs evidence to verify publication dates and corresponding
authors. Keep only the website annotations in _data/publication_annotations.json;
PDFs, Scholar exports and audit reports stay local and are not build dependencies.
Both output indexes are generated and must not be edited by hand.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIB = ROOT / "_bibliography" / "papers.bib"
OUT = ROOT / "_data" / "publications.json"
ANNOTATIONS = ROOT / "_data" / "publication_annotations.json"
TOPICS_OUT = ROOT / "_data" / "publication_topics.json"


def entries(text: str):
    cursor = 0
    start_re = re.compile(r"@(article|inproceedings|misc|book|incollection)\s*\{\s*([^,]+),", re.I)
    while match := start_re.search(text, cursor):
        depth, pos = 1, match.end()
        while pos < len(text) and depth:
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
            pos += 1
        yield match.group(1).lower(), match.group(2), text[match.start():pos]
        cursor = pos


def field(record: str, name: str) -> str:
    match = re.search(rf"(?mi)^\s*{re.escape(name)}\s*=\s*\{{(.*?)\}}\s*,?\s*$", record)
    return match.group(1).strip() if match else ""


def clean(value: str) -> str:
    value = re.sub(r"[{}]", "", value)
    value = value.replace("\\&", "&").replace("\\_", "_")
    return re.sub(r"\s+", " ", value).strip()


def people(value: str) -> list[str]:
    result = []
    for person in re.split(r"\s+and\s+", value):
        person = clean(person)
        if not person:
            continue
        if "," in person:
            last, first = [part.strip() for part in person.split(",", 1)]
            result.append(f"{first} {last}".strip())
        else:
            result.append(person)
    return result


def display_venue(value: str) -> str:
    # Scholar exports sometimes duplicate a conference acronym and year, e.g.
    # "ICASSP 2026-2026 IEEE ... (ICASSP)".
    value = re.sub(r"^ICASSP\s+(\d{4})-\1\s+", r"\1 ", value, flags=re.I)
    value = re.sub(r"\s*\(ICASSP\)\s*$", "", value, flags=re.I)
    return value


def category(entry_type: str, venue: str) -> str:
    venue_lower = venue.lower()
    if "arxiv" in venue_lower or "ssrn" in venue_lower or entry_type == "misc" and "preprint" in venue_lower:
        return "Preprints"
    if "book chapter" in venue_lower or "techniques in tracking and sensor management" in venue_lower:
        return "Book Chapters"
    if entry_type == "inproceedings" or "conference" in venue_lower or "workshop" in venue_lower:
        return "Conference Papers"
    if entry_type == "article":
        return "Journal Articles"
    return "Other Publications"


def publication_url(record: str, venue: str) -> str:
    explicit = clean(field(record, "url") or field(record, "html"))
    if re.match(r"^https?://", explicit):
        return explicit
    arxiv = re.search(r"arxiv:\s*(\d{4}\.\d{4,5}(?:v\d+)?)", venue, flags=re.I)
    return f"https://arxiv.org/abs/{arxiv.group(1)}" if arxiv else ""


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate annotation key: {key}")
        result[key] = value
    return result


def annotations(document: str, known_keys: set[str]):
    data = json.loads(document, object_pairs_hook=unique_object)
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported publication annotation schema")
    definitions = data.get("topic_definitions")
    topics = data.get("topics")
    correspondents = data.get("corresponding_authors")
    if not isinstance(definitions, list) or not definitions:
        raise ValueError("Missing topic definitions")
    if not isinstance(topics, dict) or not isinstance(correspondents, dict):
        raise ValueError("Missing topic assignments or corresponding-author annotations")
    for topic in definitions:
        if not isinstance(topic, dict) or not all(isinstance(topic.get(key), str) for key in ("id", "name", "description")):
            raise ValueError("Malformed topic definition")
        if not re.fullmatch(r"[a-z][a-z0-9-]*", topic["id"]):
            raise ValueError(f"Invalid topic ID: {topic['id']}")
    ids = {topic["id"] for topic in definitions}
    if len(ids) != len(definitions):
        raise ValueError("Duplicate topic definitions")
    for key, values in topics.items():
        if not isinstance(values, list) or not values or any(value not in ids for value in values) or len(set(values)) != len(values):
            raise ValueError(f"Unknown, empty or repeated topic for {key}: {values}")
    for key, names in correspondents.items():
        if not isinstance(names, list) or not names or any(not isinstance(name, str) or not name.strip() for name in names):
            raise ValueError(f"Empty or malformed corresponding-author names: {key}")
        if len(set(names)) != len(names):
            raise ValueError(f"Duplicate corresponding-author name: {key}")
    stale = (topics.keys() | correspondents.keys()) - known_keys
    if stale:
        raise ValueError(f"Annotation keys not found in bibliography: {sorted(stale)}")
    missing = known_keys - topics.keys()
    if missing:
        if "unclassified" not in ids:
            definitions.append({"id": "unclassified", "name": "Unclassified", "description": "Recent additions awaiting topic assignment."})
        topics.update({key: ["unclassified"] for key in missing})
        print(f"Topic assignment needed: {', '.join(sorted(missing))}")
    return definitions, topics, correspondents


def topic_index(years: list[dict], definitions: list[dict]) -> list[dict]:
    result = []
    for topic in definitions:
        filtered_years = []
        count = 0
        for year in years:
            groups = []
            for group in year["groups"]:
                items = [paper for paper in group["items"] if topic["id"] in paper["topics"]]
                if items:
                    groups.append({"name": group["name"], "items": items})
                    count += len(items)
            if groups:
                filtered_years.append({"year": year["year"], "groups": groups})
        result.append({**topic, "count": count, "years": filtered_years})
    return result


def main() -> int:
    records = list(entries(BIB.read_text(encoding="utf-8")))
    definitions, topics, correspondents = annotations(
        ANNOTATIONS.read_text(encoding="utf-8"),
        {key for _, key, _ in records},
    )
    grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    seen_ids = set()
    for entry_type, key, record in records:
        title = clean(field(record, "title"))
        year = clean(field(record, "year"))
        venue = display_venue(clean(field(record, "journal") or field(record, "booktitle") or field(record, "note")))
        if not title or not year:
            continue
        group_name = category(entry_type, venue)
        publication_id = f"{key}-{re.sub(r'[^a-z0-9]+', '-', group_name.lower()).strip('-')}"
        if publication_id in seen_ids:
            raise ValueError(f"Duplicate publication ID: {publication_id}")
        seen_ids.add(publication_id)
        authors = people(field(record, "author"))
        if set(correspondents.get(key, [])) - set(authors):
            raise ValueError(f"Corresponding author not in author list: {key}")
        item = {
            "key": key,
            "id": publication_id,
            "title": title,
            "authors": authors,
            "venue": venue,
            "abbr": clean(field(record, "abbr")),
            "doi": clean(field(record, "doi")),
            "url": publication_url(record, venue),
            "topics": topics[key],
            "corresponding_authors": correspondents.get(key, []),
        }
        grouped[year][group_name].append(item)

    order = ["Journal Articles", "Conference Papers", "Book Chapters", "Preprints", "Other Publications"]
    years = []
    for year in sorted(grouped, key=lambda value: int(value) if value.isdigit() else 0, reverse=True):
        groups = []
        for name in order:
            items = grouped[year].get(name, [])
            if items:
                groups.append({"name": name, "items": items})
        years.append({"year": year, "groups": groups})

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(years, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    TOPICS_OUT.write_text(json.dumps(topic_index(years, definitions), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} with {sum(len(group['items']) for year in years for group in year['groups'])} records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
