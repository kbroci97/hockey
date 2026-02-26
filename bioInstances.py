import csv
from sqlmodel import Session, create_engine
from models import Stats  # adjust if needed


databaseUrl = "sqlite:///database.db"  # change if using Postgres
engine = create_engine(databaseUrl)


def loadStatsFromCsv(csvPath: str):
    with Session(engine) as session:
        with open(csvPath, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            import re

            def parse_int(val):
                if val is None:
                    return None
                s = str(val).strip()
                if s == "":
                    return None
                s = re.sub(r"[^0-9\-]", "", s)
                try:
                    return int(s)
                except Exception:
                    return None

            def parse_float(val):
                if val is None:
                    return None
                s = str(val).strip()
                if s == "":
                    return None
                s = s.replace('%','')
                s = re.sub(r"[^0-9\.\-]", "", s)
                try:
                    return float(s)
                except Exception:
                    return None

            def split_player(name: str):
                if not name:
                    return (None, None)
                # remove trailing parenthetical qualifiers: "Name (R)"
                name = re.sub(r"\s*\(.*\)$", "", name).strip()
                if ',' in name:
                    parts = [p.strip() for p in name.split(',', 1)]
                    last = parts[0]
                    first = parts[1] if len(parts) > 1 else None
                    return (first, last)
                parts = name.split()
                first = parts[0] if parts else None
                last = " ".join(parts[1:]) if len(parts) > 1 else None
                return (first, last)

            def norm_row(row):
                return { (k.strip().lower() if k else k): (v.strip() if isinstance(v, str) else v) for k, v in row.items() }

            for row in reader:
                try:
                    r = norm_row(row)
                    first = r.get("firstname") or r.get("first_name")
                    last = r.get("lastname") or r.get("last_name")
                    if not first and not last:
                        player = r.get("player") or r.get("name") or ""
                        f, l = split_player(player)
                        first = first or f
                        last = last or l

                    stat = Stats(
                        firstName=first,
                        lastName=last,
                        gp=parse_int(r.get("gp") or r.get("g_p") or r.get("games_played")),
                        g=parse_int(r.get("g") or r.get("goals")),
                        a=parse_int(r.get("a") or r.get("assists")),
                        pts=parse_int(r.get("pts") or r.get("points")),
                        sh=parse_int(r.get("sh") or r.get("shots") or r.get("sog")),
                        shPercent=parse_float(r.get("shpercent") or r.get("sog%") or r.get("sog_percent")),
                        plusMinus=parse_int(r.get("plusminus") or r.get("+-") or r.get("pm")),
                        ppg=parse_int(r.get("ppg") or r.get("pp")),
                        shg=parse_int(r.get("shg")),
                        fg=parse_int(r.get("fg")),
                        gwg=parse_int(r.get("gwg")),
                        gtg=parse_int(r.get("gtg")),
                        otg=parse_int(r.get("otg")),
                        htg=parse_int(r.get("htg")),
                        uag=parse_int(r.get("uag")),
                        pnPim=r.get("pnpim") or r.get("pim") or None,
                        min=parse_int(r.get("min") or r.get("minutes")),
                        maj=parse_int(r.get("maj")),
                        oth=parse_int(r.get("oth")),
                        blk=parse_int(r.get("blk") or r.get("blocks")),
                    )

                    session.add(stat)

                except Exception as error:
                    print(f"Skipping {row.get('FirstName') or first} {row.get('LastName') or last}: {error}")
            session.commit()

    print("Stats successfully loaded.")


if __name__ == "__main__":
    loadStatsFromCsv("stats.csv")