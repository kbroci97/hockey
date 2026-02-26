#!/usr/bin/env python3
"""Scrape Mercyhurst men's hockey roster and append to bio.csv

Usage: python scripts/scrape_roster.py
"""
from __future__ import annotations
import csv
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://hurstathletics.com"
ROSTER_URL = "https://hurstathletics.com/sports/mens-ice-hockey/roster"
CSV_PATH = "bio.csv"
FIELDNAMES = [
    "firstName",
    "lastName",
    "position",
    "jerseyNumber",
    "weight",
    "height",
    "classYear",
    "hometown",
    "highSchool",
]


def text_or_none(el) -> Optional[str]:
    return el.get_text(strip=True) if el else None


def parse_player_page(html: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    # Name
    name_el = soup.find(class_="sidearm-roster-player-name")
    first, last = (None, None)
    if name_el:
        spans = name_el.find_all("span")
        texts = [s.get_text(strip=True) for s in spans if s.get_text(strip=True)]
        if len(texts) >= 2:
            first, last = texts[0], texts[1]
        elif len(texts) == 1:
            parts = texts[0].split()
            first = parts[0]
            last = " ".join(parts[1:]) if len(parts) > 1 else None

    # Jersey
    jersey_el = soup.find(class_="sidearm-roster-player-jersey-number")
    jersey = None
    if jersey_el:
        j = jersey_el.get_text(strip=True)
        jersey = re.sub(r"[^0-9]", "", j) or None

    # Fields mapping from dt -> dd
    fields = {}
    for dt in soup.find_all("dt"):
        key = dt.get_text(strip=True).rstrip(":")
        dd = dt.find_next_sibling("dd")
        if not dd:
            # sometimes dt and dd are wrapped differently
            parent = dt.parent
            dd = parent.find("dd") if parent else None
        fields[key] = text_or_none(dd)

    result = {
        "firstName": first,
        "lastName": last,
        "position": fields.get("Position") or fields.get("Pos") or None,
        "jerseyNumber": jersey,
        "weight": fields.get("Weight"),
        "height": fields.get("Height"),
        "classYear": fields.get("Class"),
        "hometown": fields.get("Hometown"),
        "highSchool": fields.get("High School"),
    }
    return result


def get_player_urls() -> List[str]:
    r = requests.get(ROSTER_URL, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    links = []
    # player links include '/sports/mens-ice-hockey/roster/slug/number'
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/sports/mens-ice-hockey/roster/" in href and href.strip() != "#":
            full = urljoin(BASE, href)
            if full not in links:
                links.append(full)
    # Heuristic: keep only links that look like player detail pages (not team or filters)
    filtered = [u for u in links if re.search(r"/roster/[^/]+/\d+", u)]
    return filtered or links


def read_existing_names(csv_path=CSV_PATH) -> set:
    seen = set()
    try:
        with open(csv_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for r in reader:
                fn = r.get("firstName")
                ln = r.get("lastName")
                if fn and ln:
                    seen.add((fn.strip().lower(), ln.strip().lower()))
    except FileNotFoundError:
        pass
    return seen


def append_rows(rows: List[Dict[str, Optional[str]]], csv_path=CSV_PATH):
    # ensure header exists
    try:
        with open(csv_path, "r", encoding="utf-8") as fh:
            has_header = True
    except FileNotFoundError:
        has_header = False

    with open(csv_path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        if not has_header:
            writer.writeheader()
        for row in rows:
            # Normalize None -> empty string
            out = {k: (v if v is not None else "") for k, v in row.items()}
            writer.writerow(out)


def main():
    print("Fetching roster page...")
    urls = get_player_urls()
    print(f"Found {len(urls)} candidate player pages.")
    seen = read_existing_names()
    new_rows = []
    for url in urls:
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
        except Exception as e:
            print(f"Skipping {url}: {e}")
            continue
        data = parse_player_page(r.text)
        key = (data.get("firstName") or "", data.get("lastName") or "")
        key_norm = (key[0].strip().lower(), key[1].strip().lower())
        if key_norm in seen:
            print(f"Skipping existing player {key[0]} {key[1]}")
            continue
        if not key[0] or not key[1]:
            print(f"Skipping incomplete name for {url}")
            continue
        new_rows.append(data)
        seen.add(key_norm)
        print(f"Added {key[0]} {key[1]}")

    if new_rows:
        append_rows(new_rows)
        print(f"Appended {len(new_rows)} new rows to {CSV_PATH}.")
    else:
        print("No new players to append.")


if __name__ == "__main__":
    main()
