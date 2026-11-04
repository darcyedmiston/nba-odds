"""One-off: do historical AU player props exist for a 2025-26 game? Costs at most 51 credits."""
import json
import os
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta

API = "https://api.the-odds-api.com/v4/historical/sports/basketball_nba"
KEY = os.environ["ODDS_API_KEY"]
MARKETS = "player_points,player_rebounds,player_assists,player_threes,player_points_rebounds_assists"


def get(path, **params):
    url = f"{API}{path}?{urllib.parse.urlencode(dict(params, apiKey=KEY), safe=',')}"
    with urllib.request.urlopen(url, timeout=60) as r:
        print("cost", r.headers.get("x-requests-last"), "remaining", r.headers.get("x-requests-remaining"))
        return json.load(r)


events = get("/events", date="2026-01-15T22:00:00Z")["data"]
print(len(events), "events at snapshot")
e = sorted(events, key=lambda x: x["commence_time"])[0]
tip = datetime.fromisoformat(e["commence_time"].replace("Z", "+00:00"))
snap = (tip - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
print(e["away_team"], "@", e["home_team"], e["commence_time"], "snapshot", snap)
data = get(f"/events/{e['id']}/odds", date=snap, regions="au", markets=MARKETS, oddsFormat="decimal")
print("snapshot actually returned:", data.get("timestamp"))
books = data["data"].get("bookmakers", [])
print("books:", [b["key"] for b in books])
for b in books:
    c = Counter(m["key"] for m in b["markets"] for _ in m["outcomes"])
    both = {}
    for m in b["markets"]:
        for o in m["outcomes"]:
            both.setdefault((m["key"], o.get("description"), o.get("point")), set()).add(o["name"])
    two = sum(v == {"Over", "Under"} for v in both.values())
    print(b["key"], dict(c), "players", len({k[1] for k in both}), "two-sided lines", two, "of", len(both))
