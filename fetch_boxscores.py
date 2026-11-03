"""Pull NBA box scores for Melbourne slates and save every player's line
as a flat CSV for the 6pm evening review.

    python fetch_boxscores.py          # catch up: any slate from the last 7 days not yet fully Final
    python fetch_boxscores.py 2        # the same, and always re-pull the slate from 2 days ago

GitHub's scheduled runs can start many hours late, often after Melbourne
midnight, when "today" is a new slate nobody has played yet. So a slate with no
games started is not an error, and each run catches up on whatever is missing.

Source: ESPN's public scoreboard + game-summary JSON (no key needed).
The official NBA box score PDFs (statsdmz.nba.com) remain the
cross-check for anything within 1 of the line.

Output: boxscores/<melb date>.csv and boxscores/latest.csv with columns
date_melb, game_id, game, status, team, player, starter, minutes,
pts, reb, ast, threes, pra, ra, final_score

A game with no box score yet gets one row with a blank player and a status such
as "Scheduled", so settle.py knows the slate isn't finished.
"""
import csv
import sys
from datetime import timedelta
from pathlib import Path

from nbalib import ESPN, get_json, melb_to_us, today_melb

LOOKBACK_DAYS = 7
OUT = Path("boxscores")
NEVER_PLAYED = ("POSTPONED", "CANCELED", "CANCELLED")
FIELDS = ["date_melb", "game_id", "game", "status", "team", "player",
          "starter", "minutes", "pts", "reb", "ast", "threes", "pra", "ra",
          "final_score"]


def to_int(v):
    try:
        return int(str(v).split("-")[0])
    except (TypeError, ValueError):
        return 0


def pull(target):
    """A Melbourne date's slate is the previous US (ET) date's games.

    Returns (rows, finals, n_games, missing), where missing lists finished
    games that have no player lines.
    """
    us_date = melb_to_us(target).strftime("%Y%m%d")
    board = get_json(f"{ESPN}/scoreboard?dates={us_date}&limit=50")
    rows, finals, missing = [], 0, []
    events = board.get("events", [])
    for ev in events:
        comp = ev["competitions"][0]
        status = comp["status"]["type"]
        completed = bool(status.get("completed"))
        finals += completed
        teams = {c["homeAway"]: c for c in comp["competitors"]}
        away, home = teams["away"]["team"]["abbreviation"], teams["home"]["team"]["abbreviation"]
        game = f"{away} @ {home}"
        score = f"{away} {teams['away'].get('score')} - {home} {teams['home'].get('score')}"
        n_before = len(rows)
        summary = get_json(f"{ESPN}/summary?event={ev['id']}")
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
        if len(rows) == n_before and not any(w in status.get("name", "").upper() for w in NEVER_PLAYED):
            desc = status.get("description") or "Scheduled"
            if completed:
                missing.append(game)
                desc = "Missing box score"
            rows.append({"date_melb": target.isoformat(), "game_id": ev["id"], "game": game,
                         "status": desc, "team": "", "player": "", "starter": "", "minutes": "",
                         "pts": "", "reb": "", "ast": "", "threes": "", "pra": "", "ra": "",
                         "final_score": score})
    return rows, finals, len(events), missing


def is_complete(target):
    """True if this slate's file exists and every row is Final."""
    path = OUT / f"{target.isoformat()}.csv"
    if not path.exists():
        return False
    with open(path) as f:
        rows = list(csv.DictReader(f))
    return bool(rows) and all(r["status"].startswith("Final") for r in rows)


def save(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "auto"
    forced = None if arg == "auto" else int(arg)
    today = today_melb()
    OUT.mkdir(exist_ok=True)
    problems, newest = [], None
    for back in range(max(LOOKBACK_DAYS, forced or 0), -1, -1):
        target = today - timedelta(days=back)
        if back != forced and is_complete(target):
            continue
        try:
            rows, finals, n, missing = pull(target)
        except Exception as e:
            problems.append(f"{target}: pull failed ({e})")
            continue
        played = [r for r in rows if r["player"]]
        print(f"{target}: {n} games, {finals} final, {len(played)} player rows")
        problems += [f"{target}: {g} is finished but has no box score" for g in missing]
        if not played:
            continue  # no games, or none started yet: leave any existing file alone
        save(OUT / f"{target.isoformat()}.csv", rows)
        newest = rows
    if newest:
        save(OUT / "latest.csv", newest)
    if problems:
        sys.exit("\n".join(problems))


if __name__ == "__main__":
    main()
