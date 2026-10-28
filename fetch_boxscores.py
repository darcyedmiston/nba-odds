"""Pull official NBA box scores for the latest Melbourne slate and save
every player's line as a flat CSV for the 6pm evening review.

Source: the NBA's own public CDN (the same JSON nba.com uses), so no API
key is needed. Runs in GitHub Actions because the cloud review session
cannot reach cdn.nba.com directly.

Output: boxscores/<melb date>.csv and boxscores/latest.csv with columns
date_melb, game_id, game, status, team, player, starter, minutes,
pts, reb, ast, threes, pra, ra, final_score
"""
import csv
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

CDN = "https://cdn.nba.com/static/json"
MELB = timezone(timedelta(hours=11))  # AEDT; switch to +10 in April
UA = {"User-Agent": "Mozilla/5.0 (nba-odds box score pull)"}
FIELDS = ["date_melb", "game_id", "game", "status", "team", "player",
          "starter", "minutes", "pts", "reb", "ast", "threes", "pra", "ra",
          "final_score"]


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def minutes(iso):
    # "PT32M40.00S" -> "32:40"
    m = re.match(r"PT(\d+)M([\d.]+)S", iso or "")
    if not m:
        return "0:00"
    return f"{int(m.group(1))}:{int(float(m.group(2))):02d}"


def slate_games(days_back):
    """Games whose tip-off fell on the Melbourne date `days_back` days ago
    (0 = today in Melbourne)."""
    target = (datetime.now(MELB) - timedelta(days=days_back)).date()
    sched = get(f"{CDN}/staticData/scheduleLeagueV2.json")
    games = []
    for day in sched["leagueSchedule"]["gameDates"]:
        for g in day["games"]:
            tip = g.get("gameDateTimeUTC")
            if not tip:
                continue
            tip = datetime.fromisoformat(tip.replace("Z", "+00:00"))
            if tip.astimezone(MELB).date() == target:
                games.append(g)
    return target, games


def main():
    days_back = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    target, games = slate_games(days_back)
    rows, finals = [], 0
    for g in games:
        gid = g["gameId"]
        try:
            box = get(f"{CDN}/liveData/boxscore/boxscore_{gid}.json")["game"]
        except Exception as e:  # game not started yet, or CDN hiccup
            print(f"skip {gid}: {e}")
            continue
        away, home = box["awayTeam"], box["homeTeam"]
        game = f"{away['teamTricode']} @ {home['teamTricode']}"
        status = box.get("gameStatusText", "")
        finals += box.get("gameStatus") == 3
        score = f"{away['teamTricode']} {away['score']} - {home['teamTricode']} {home['score']}"
        for team in (away, home):
            for p in team["players"]:
                s = p.get("statistics", {})
                pts, reb, ast = s.get("points", 0), s.get("reboundsTotal", 0), s.get("assists", 0)
                rows.append({
                    "date_melb": target.isoformat(),
                    "game_id": gid,
                    "game": game,
                    "status": status if p.get("played") == "1" else f"{status} / DNP {p.get('notPlayingReason', '')}".strip(),
                    "team": team["teamTricode"],
                    "player": p["name"],
                    "starter": p.get("starter", "0"),
                    "minutes": minutes(s.get("minutes")),
                    "pts": pts, "reb": reb, "ast": ast,
                    "threes": s.get("threePointersMade", 0),
                    "pra": pts + reb + ast, "ra": reb + ast,
                    "final_score": score,
                })

    out = Path("boxscores")
    out.mkdir(exist_ok=True)
    for path in (out / f"{target.isoformat()}.csv", out / "latest.csv"):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
    print(f"{target}: {len(games)} games, {finals} final, {len(rows)} player rows")


if __name__ == "__main__":
    main()
