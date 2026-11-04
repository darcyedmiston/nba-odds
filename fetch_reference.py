"""Save one morning snapshot of non-AU NBA prop prices, for the shadow report only.

    python fetch_reference.py

Writes odds/reference/<date_melb>.csv. model.py never reads this folder, so it can't change a
pick. Only games tipping within HOURS are pulled, so an afternoon run doesn't lock in an early
price, and a slate already saved is never pulled again. Skips the whole pull if credits are short.
"""
import csv
import json
import os
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

API = "https://api.the-odds-api.com/v4/sports/basketball_nba"
MARKETS = ("player_points,player_rebounds,player_assists,player_threes,"
           "player_points_rebounds_assists")
BOOKS = ("fanduel", "draftkings", "betonlineag")
EXCHANGES = ("novig", "prophetx", "polymarket")
MELB = ZoneInfo("Australia/Melbourne")
OUT = Path("odds/reference")
FIELDS = ["date_melb", "tipoff_melb", "game", "bookmaker", "market", "player", "side", "line",
          "odds", "last_update"]
DAILY_RESERVE = 150  # credits per day left to the reset that the main pipeline keeps


def credit_floor(now):
    """Credits to hold back until the plan resets on the 1st of next month."""
    first = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
    return DAILY_RESERVE * max((first.date() - now.date()).days, 0)


def tip_of(event):
    return datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00"))


def select_games(events, now, hours, saved):
    """Games tipping within `hours` whose Melbourne slate has no saved snapshot."""
    games = [e for e in events if now <= tip_of(e) <= now + timedelta(hours=hours)]
    return [e for e in games if tip_of(e).astimezone(MELB).strftime("%Y-%m-%d") not in saved]


def flatten(event, data):
    tip = tip_of(event).astimezone(MELB)
    rows = []
    for book in data.get("bookmakers", []):
        for market in book.get("markets", []):
            for o in market.get("outcomes", []):
                rows.append({"date_melb": tip.strftime("%Y-%m-%d"), "tipoff_melb": tip.strftime("%H:%M"),
                             "game": f"{event['away_team']} @ {event['home_team']}",
                             "bookmaker": book["key"], "market": market["key"],
                             "player": o.get("description", ""), "side": o["name"],
                             "line": o.get("point", ""), "odds": o["price"],
                             "last_update": market.get("last_update", "")})
    return rows


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r), r.headers.get("x-requests-remaining"), r.headers.get("x-requests-last")


def main():
    key = os.environ["ODDS_API_KEY"]
    now = datetime.now(timezone.utc)
    hours = float(os.environ.get("REFERENCE_HOURS", 12))
    max_games = int(os.environ.get("REFERENCE_MAX_GAMES", 99))
    dry_run = os.environ.get("REFERENCE_DRY_RUN") == "1"
    events, remaining, _ = get(f"{API}/events?apiKey={key}")
    floor = credit_floor(now)
    if remaining is not None and float(remaining) < floor:
        print(f"skipped: {remaining} credits left, keeping {floor} for the main pipeline")
        return 0
    saved = {p.stem for p in OUT.glob("*.csv")}
    games = select_games(events, now, hours, saved)[:max_games]
    by_day, credits = defaultdict(list), 0
    for e in games:
        data, remaining, used = get(f"{API}/events/{e['id']}/odds?apiKey={key}"
                                    f"&bookmakers={','.join(BOOKS + EXCHANGES)}"
                                    f"&markets={MARKETS}&oddsFormat=decimal")
        credits += int(used or 0)
        rows = flatten(e, data)
        print(f"{e['away_team']} @ {e['home_team']}: {len(rows)} prices, "
              f"books {sorted({r['bookmaker'] for r in rows})}, credits {used}")
        if rows:
            by_day[rows[0]["date_melb"]].extend(rows)
    print(f"{len(games)} games, credits used {credits}, remaining {remaining}")
    if dry_run:
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for day, rows in by_day.items():
        with open(OUT / f"{day}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
