#!/usr/bin/env python3
import csv
import sqlite3
import os
from pathlib import Path


def create_table_from_headers(cur, table_name, headers):
    cols = [f'"{h}" TEXT' for h in headers]
    cols_sql = ', '.join(cols)
    cur.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    cur.execute(f'CREATE TABLE "{table_name}" ({cols_sql})')


def import_csv_to_table(db_path, csv_path, table_name):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if not headers:
            print(f'No headers found in {csv_path}')
            return 0

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        create_table_from_headers(cur, table_name, headers)

        placeholders = ','.join(['?'] * len(headers))
        cols_quoted = ','.join([f'"{h}"' for h in headers])
        insert_sql = f'INSERT INTO "{table_name}" ({cols_quoted}) VALUES ({placeholders})'

        rows = []
        for row in reader:
            rows.append([row.get(h, None) for h in headers])

        if rows:
            cur.executemany(insert_sql, rows)
            conn.commit()

        count = cur.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
        conn.close()
        return count


def main():
    base = Path(__file__).resolve().parents[1]
    bio_csv = base / 'bio.csv'
    stats_csv = base / 'stats.csv'
    db_path = base / 'hockey.db'

    if not bio_csv.exists() or not stats_csv.exists():
        print('Required CSV files not found in workspace root.')
        print(f'Looking for: {bio_csv} and {stats_csv}')
        return

    if db_path.exists():
        backup = base / 'hockey.db.bak'
        print(f'Existing {db_path} found — moving to {backup}')
        if backup.exists():
            backup.unlink()
        db_path.rename(backup)

    print('Importing bio.csv...')
    bio_count = import_csv_to_table(str(db_path), str(bio_csv), 'bio')
    print(f'Inserted {bio_count} rows into table "bio"')

    print('Importing stats.csv...')
    stats_count = import_csv_to_table(str(db_path), str(stats_csv), 'stats')
    print(f'Inserted {stats_count} rows into table "stats"')

    print('Done. Database created at:', db_path)


if __name__ == '__main__':
    main()
