#!/usr/bin/env python3
"""Find the skaters table headers (containing GP, G, A) and write them to stats.csv
"""
from __future__ import annotations
import requests
from bs4 import BeautifulSoup
import csv

URL = "https://hurstathletics.com/sports/mens-ice-hockey/stats/2025-26#team"
OUT = "stats.csv"
TARGET = {"gp", "g", "a"}


def get_all_table_headers(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    team = soup.find(id="team") or soup
    headers_list = []
    for table in team.find_all("table"):
        headers = [th.get_text(strip=True) for th in table.select("thead th")]
        if not headers:
            first = table.find("tr")
            if first:
                headers = [cell.get_text(strip=True) for cell in first.find_all(["th","td"]) ]
        if headers:
            headers_list.append(headers)
    return headers_list


def find_skaters_headers(headers_list):
    for headers in headers_list:
        low = {h.strip().lower() for h in headers}
        if TARGET.issubset(low):
            return headers
    # fallback: return the longest headers list
    return max(headers_list, key=lambda h: len(h)) if headers_list else []


def write_csv_header(headers, out_path=OUT):
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)


def main():
    headers_list = get_all_table_headers(URL)
    chosen = find_skaters_headers(headers_list)
    if not chosen:
        print("No headers found.")
        return
    write_csv_header(chosen)
    print("Wrote skater headers to", OUT)

if __name__ == "__main__":
    main()
