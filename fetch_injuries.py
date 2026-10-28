"""Pull the current NBA injury list (ESPN public JSON) to data/injuries/latest.csv.

Columns: team_name, player, player_key, status, detail, updated.
status is ESPN's wording: Out, Doubtful, Questionable, Day-To-Day, Probable.
"""
import csv
from pathlib import Path

from nbalib import ESPN, get_json, norm_name


def main():
    data = get_json(f"{ESPN}/injuries")
    rows = []
    for team in data.get("injuries", []):
        tname = team.get("displayName", "")
        for inj in team.get("injuries", []):
            ath = inj.get("athlete", {})
            name = ath.get("displayName", "")
            if not name:
                continue
            rows.append({
                "team_name": tname or ath.get("team", {}).get("displayName", ""),
                "player": name,
                "player_key": norm_name(name),
                "status": inj.get("status", ""),
                "detail": (inj.get("shortComment") or inj.get("longComment") or "")[:200].replace("\n", " "),
                "updated": inj.get("date", ""),
            })
    out = Path("data/injuries")
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "latest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["team_name", "player", "player_key", "status", "detail", "updated"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} injury entries across {len(data.get('injuries', []))} teams")


if __name__ == "__main__":
    main()
