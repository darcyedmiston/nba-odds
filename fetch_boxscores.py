"""Pull NBA box scores for a Melbourne slate and save every player's line
as a flat CSV for the 6pm evening review.

Source: ESPN's public scoreboard + game-summary JSON (no key needed).
The official NBA box score PDFs (statsdmz.nba.com) remain the
cross-check for anything within 1 of the line.

Output: boxscores/<melb date>.csv and boxscores/latest.csv with columns
date_melb, game_id, game, status, team, player, starter, minutes,
pts, reb, ast, threes, pra, ra, final_score
"""
import csv
import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ESPN = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
MELB = timezone(timedelta(hours=11))  # AEDT; switch to +10 in April
UA = {"User-Agent": "nba-odds box score pull (github.com/darcyedmiston/nba-odds)"}
FIELDS = ["date_melb", "game_id", "game", "status", "team", "player",
          "starter", "minutes", "pts", "reb", "ast", "threes", "pra", "ra",
          "final_score"]


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def to_int(v):
    try:
        return int(str(v).split("-")[0])
    except (TypeError, ValueError):
        return 0


def pull(target):
    """A Melbourne date's slate is the previous US (ET) date's games."""
    us_date = (target - timedelta(days=1)).strftime("%Y%m%d")
    board = get(f"{ESPN}/scoreboard?dates={us_date}")
    rows, finals = [], 0
    events = board.get("events", [])
    for ev in events:
        comp = ev["competitions"][0]
        status = comp["status"]["type"]
        finals += bool(status.get("completed"))
        teams = {c["homeAway"]: c for c in comp["competitors"]}
        away, home = teams["away"]["team"]["abbreviation"], teams["home"]["team"]["abbreviation"]
        game = f"{away} @ {home}"
        score = f"{away} {teams['away'].get('score')} - {home} {teams['home'].get('score')}"
        summary = get(f"{ESPN}/summary?event={ev['id']}")
        for team in summary.get("boxscore", {}).get("players", []):
            abbr = team["team"]["abbreviation"]
            for block in team.get("statistics", []):
                keys = block.get("keys", [])
                for a in block.get("athletes", []):
                    st = dict(zip(keys, a.get("stats", [])))
                    dnp = bool(a.get("didNotPlay")) or not st
                    pts = 0 if dnp else to_int(st.get("points"))
                    reb = 0 if dnp else to_int(st.get("rebounds"))
                    ast = 0 if dnp else to_int(st.get("assists"))
                    threes = 0 if dnp else to_int(
                        st.get("threePointFieldGoalsMade-threePointFieldGoalsAttempted"))
                    desc = status.get("description", "")
                    if dnp:
                        desc = f"{desc} / DNP {a.get('reason', '')}".strip()
                    rows.append({
                        "date_melb": target.isoformat(),
                        "game_id": ev["id"],
                        "game": game,
                        "status": desc,
                        "team": abbr,
                        "player": a["athlete"]["displayName"],
                        "starter": "1" if a.get("starter") else "0",
                        "minutes": "0" if dnp else st.get("minutes", "0"),
                        "pts": pts, "reb": reb, "ast": ast, "threes": threes,
                        "pra": pts + reb + ast, "ra": reb + ast,
                        "final_score": score,
                    })
    return rows, finals, len(events)


def main():
    days_back = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    target = (datetime.now(MELB) - timedelta(days=days_back)).date()
    rows, finals, n = pull(target)
    out = Path("boxscores")
    out.mkdir(exist_ok=True)
    for path in (out / f"{target.isoformat()}.csv", out / "latest.csv"):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
    print(f"{target}: {n} games, {finals} final, {len(rows)} player rows")
    if n and not rows:
        sys.exit("games found but no player rows - check the source")


if __name__ == "__main__":
    main()
