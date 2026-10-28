"""Capture closing lines for CLV.

Started once a day (by the 9:35am pre-tip check) with the teams that have
picks. For each of those games it waits until LEAD_MIN minutes before
tip-off, pulls that game's AU prop lines from The Odds API, and commits
them straight away, so every game's close is saved even if a later one
fails.

Output: odds/closing/<melb date>.csv - same columns as odds/latest.csv
plus captured_utc and minutes_to_tip.
"""
import csv
import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://api.the-odds-api.com/v4/sports/basketball_nba"
KEY = os.environ["ODDS_API_KEY"]
MARKETS = "player_points,player_rebounds,player_assists,player_threes,player_points_rebounds_assists"
MELB = timezone(timedelta(hours=11))  # AEDT; switch to +10 in April
LEAD_MIN = int(os.environ.get("LEAD_MIN", "5"))
FIELDS = ["date_melb", "tipoff_melb", "game", "bookmaker", "market", "player",
          "side", "line", "odds", "last_update", "captured_utc", "minutes_to_tip"]


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r), r.headers.get("x-requests-remaining"), r.headers.get("x-requests-last")


def commit(path, msg):
    subprocess.run(["git", "add", str(path), "odds/credits.json"], check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        return
    subprocess.run(["git", "commit", "-q", "-m", msg], check=True)
    for _ in range(3):  # another workflow may have pushed meanwhile
        subprocess.run(["git", "pull", "-q", "--rebase"], check=False)
        if subprocess.run(["git", "push", "-q"]).returncode == 0:
            return
        time.sleep(10)
    raise SystemExit("push failed")


def main():
    wanted = [t.strip().lower() for t in os.environ.get("GAMES", "").split(",") if t.strip()]
    now = datetime.now(timezone.utc)
    events, _, _ = get(f"{API}/events?apiKey={KEY}")  # free endpoint
    slate = []
    for e in events:
        tip = datetime.fromisoformat(e["commence_time"].replace("Z", "+00:00"))
        teams = f"{e['home_team']} {e['away_team']}".lower()
        if now < tip <= now + timedelta(hours=12) and (not wanted or any(w in teams for w in wanted)):
            slate.append((tip, e))
    slate.sort(key=lambda x: x[0])
    print(f"{len(slate)} games to capture: " +
          ", ".join(f"{e['away_team']} @ {e['home_team']} {t.astimezone(MELB):%H:%M}" for t, e in slate))
    if not slate:
        return

    stamp = slate[0][0].astimezone(MELB).strftime("%Y-%m-%d")
    out = Path("odds/closing")
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{stamp}.csv"
    if not path.exists():
        with open(path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()

    for tip, e in slate:
        wait = (tip - timedelta(minutes=LEAD_MIN) - datetime.now(timezone.utc)).total_seconds()
        if wait > 0:
            print(f"waiting {wait / 60:.0f} min for {e['away_team']} @ {e['home_team']}")
            time.sleep(wait)
        if datetime.now(timezone.utc) >= tip:
            print(f"missed tip for {e['id']}, skipping")
            continue
        try:
            data, remaining, used = get(f"{API}/events/{e['id']}/odds?apiKey={KEY}"
                                        f"&regions=au&markets={MARKETS}&oddsFormat=decimal")
        except Exception as err:  # keep going for the other games
            print(f"pull failed for {e['id']}: {err}")
            continue
        captured = datetime.now(timezone.utc)
        rows = []
        for book in data.get("bookmakers", []):
            for m in book.get("markets", []):
                for o in m.get("outcomes", []):
                    rows.append({
                        "date_melb": tip.astimezone(MELB).strftime("%Y-%m-%d"),
                        "tipoff_melb": tip.astimezone(MELB).strftime("%H:%M"),
                        "game": f"{e['away_team']} @ {e['home_team']}",
                        "bookmaker": book["key"], "market": m["key"],
                        "player": o.get("description", ""), "side": o["name"],
                        "line": o.get("point", ""), "odds": o["price"],
                        "last_update": m.get("last_update", ""),
                        "captured_utc": captured.isoformat(timespec="seconds"),
                        "minutes_to_tip": round((tip - captured).total_seconds() / 60, 1),
                    })
        with open(path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writerows(rows)
        with open("odds/credits.json", "w") as f:
            json.dump({"checked_utc": captured.isoformat(timespec="seconds"),
                       "used_this_run": int(used or 0), "remaining": remaining,
                       "filtered": True, "source": "closing"}, f, indent=1)
        print(f"captured {len(rows)} prices for {e['away_team']} @ {e['home_team']}, credits left {remaining}")
        commit(path, f"Closing lines {e['away_team']} @ {e['home_team']} {stamp}")


if __name__ == "__main__":
    main()
