"""Build / update the player game-log database from ESPN box scores.

    python build_gamelogs.py --season 2025-26     # backfill a whole regular season
    python build_gamelogs.py --recent 4           # add any finished games from the last 4 US days

Writes data/gamelogs/<season>.csv (regular season only, one row per player per game,
DNPs included with dnp=1). Already-stored games are skipped, so reruns are cheap.
"""
import argparse
import csv
import time
from datetime import date, timedelta
from pathlib import Path

from nbalib import ESPN, get_json, norm_name, season_of, today_melb, melb_to_us

FIELDS = ["season", "date_us", "game_id", "team", "team_name", "opp", "opp_name", "home",
          "player_id", "player", "player_key", "starter", "dnp", "min",
          "pts", "reb", "ast", "threes", "pra", "team_pts", "opp_pts"]
OUT = Path("data/gamelogs")


def to_int(v):
    try:
        return int(str(v).split("-")[0])
    except (TypeError, ValueError):
        return 0


def load(season):
    path = OUT / f"{season}.csv"
    if not path.exists():
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def save(season, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    rows.sort(key=lambda r: (r["date_us"], r["game_id"], r["team"], r["player"]))
    with open(OUT / f"{season}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def game_rows(event_id, d_us, season):
    summ = get_json(f"{ESPN}/summary?event={event_id}")
    comp = summ["header"]["competitions"][0]
    teams = {}
    for c in comp["competitors"]:
        teams[c["team"]["abbreviation"]] = {
            "name": c["team"]["displayName"], "home": c["homeAway"] == "home",
            "score": to_int(c.get("score")),
        }
    abbrs = list(teams)
    rows = []
    for block in summ.get("boxscore", {}).get("players", []):
        team = block["team"]["abbreviation"]
        opp = [a for a in abbrs if a != team][0]
        for stat in block.get("statistics", []):
            keys = stat.get("keys", [])
            for a in stat.get("athletes", []):
                st = dict(zip(keys, a.get("stats", [])))
                dnp = bool(a.get("didNotPlay")) or not st or to_int(st.get("minutes")) == 0
                pts, reb, ast = (0, 0, 0) if dnp else (to_int(st.get("points")), to_int(st.get("rebounds")),
                                                        to_int(st.get("assists")))
                rows.append({
                    "season": season, "date_us": d_us.isoformat(), "game_id": event_id,
                    "team": team, "team_name": teams[team]["name"],
                    "opp": opp, "opp_name": teams[opp]["name"],
                    "home": int(teams[team]["home"]),
                    "player_id": a["athlete"].get("id", ""), "player": a["athlete"]["displayName"],
                    "player_key": norm_name(a["athlete"]["displayName"]),
                    "starter": int(bool(a.get("starter"))), "dnp": int(dnp),
                    "min": 0 if dnp else to_int(st.get("minutes")),
                    "pts": pts, "reb": reb, "ast": ast,
                    "threes": 0 if dnp else to_int(st.get("threePointFieldGoalsMade-threePointFieldGoalsAttempted")),
                    "pra": pts + reb + ast,
                    "team_pts": teams[team]["score"], "opp_pts": teams[opp]["score"],
                })
    return rows


def update(dates):
    by_season, have, added = {}, {}, 0
    for d in dates:
        season = season_of(d)
        if season not in by_season:
            by_season[season] = load(season)
            have[season] = {r["game_id"] for r in by_season[season]}
        board = get_json(f"{ESPN}/scoreboard?dates={d:%Y%m%d}&limit=50")
        for ev in board.get("events", []):
            if ev.get("season", {}).get("type") != 2:  # regular season only
                continue
            if not ev["competitions"][0]["status"]["type"].get("completed"):
                continue
            if ev["id"] in have[season]:
                continue
            try:
                rows = game_rows(ev["id"], d, season)
            except Exception as e:
                print(f"  skip {ev['id']} ({d}): {e}")
                continue
            by_season[season].extend(rows)
            have[season].add(ev["id"])
            added += 1
            time.sleep(0.15)
        time.sleep(0.1)
    for season, rows in by_season.items():
        save(season, rows)
        print(f"{season}: {len({r['game_id'] for r in rows})} games, {len(rows)} player rows")
    print(f"added {added} games")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", help="backfill a whole season, e.g. 2025-26")
    ap.add_argument("--recent", type=int, default=0, help="update the last N US days")
    args = ap.parse_args()
    yesterday_us = melb_to_us(today_melb())
    dates = []
    if args.season:
        y = int(args.season[:4])
        d, end = date(y, 10, 1), min(date(y + 1, 4, 30), yesterday_us)
        while d <= end:
            dates.append(d)
            d += timedelta(days=1)
    if args.recent:
        dates += [yesterday_us - timedelta(days=i) for i in range(args.recent)]
    update(sorted(set(dates)))


if __name__ == "__main__":
    main()
