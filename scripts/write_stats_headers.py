#!/usr/bin/env python3
"""Fetch the team's stats page, pick the most complete table (skaters),
remove unwanted headers and write the header row into stats.csv.
"""
from __future__ import annotations
import requests
from bs4 import BeautifulSoup
import csv

URL = "https://hurstathletics.com/sports/mens-ice-hockey/stats/2025-26#team"
OUT = "stats.csv"
BANNED = {"shots", "goals", "penanties"}  # case-insensitive removal


def get_tables_headers(url):
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


def choose_largest(headers_list):
    if not headers_list:
        return []
    return max(headers_list, key=lambda h: len(h))


def filter_headers(headers):
    out = []
    for h in headers:
        if h.strip().lower() in BANNED:
            continue
        out.append(h)
    return out


def write_csv_header(headers, out_path=OUT):
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)


def main():
    headers_list = get_tables_headers(URL)
    chosen = choose_largest(headers_list)
    filtered = filter_headers(chosen)
    if not filtered:
        print("No headers found or all headers filtered out.")
        return
    write_csv_header(filtered)
    print("Wrote headers to", OUT)

if __name__ == "__main__":
    main()
