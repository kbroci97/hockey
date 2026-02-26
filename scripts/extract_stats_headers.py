#!/usr/bin/env python3
"""Fetch stats page and print table headers found in the #team section.
"""
from __future__ import annotations
import re
import sys
import requests
from bs4 import BeautifulSoup

URL = "https://hurstathletics.com/sports/mens-ice-hockey/stats/2025-26#team"


def extract_headers():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    team = soup.find(id="team")
    if not team:
        # fallback: search for element that contains "Team Statistics" or similar
        for el in soup.find_all():
            if el.get_text(strip=True).lower().startswith("team"):
                team = el
                break
    if not team:
        print("Could not find #team section", file=sys.stderr)
        sys.exit(2)

    tables = team.find_all("table")
    results = []
    for i, table in enumerate(tables, start=1):
        headers = [th.get_text(strip=True) for th in table.select("thead th")]
        # If no thead, try first row
        if not headers:
            first_row = table.find("tr")
            if first_row:
                headers = [td.get_text(strip=True) for td in first_row.find_all(["th","td"]) ]
        # attempt to find a nearby label for the table (like a tab label)
        label = None
        parent = table
        for _ in range(4):
            parent = parent.parent
            if not parent:
                break
            text = parent.get("data-tab") or parent.get("aria-label") or parent.get("class")
            if text:
                label = str(text)
                break
        results.append((label or f"table_{i}", headers))
    return results


def main():
    res = extract_headers()
    for label, headers in res:
        print("LABEL:", label)
        print("HEADERS:")
        print(",".join(headers))
        print()

if __name__ == "__main__":
    main()
