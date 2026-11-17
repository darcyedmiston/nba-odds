"""Calibration-by-side test (analysis only - does not touch model.py, weights or thresholds).

Question: if model probabilities are recalibrated separately for Overs and Unders (isotonic),
and bets are chosen on calibrated probability vs fair (no-vig) odds, does out-of-sample ROI
beat the current tier rule?

Method: walk-forward by Melbourne date. For each test day, fit on every earlier day
(minimum MIN_TRAIN_DAYS), predict that day only. No look-ahead.

Usage: python analysis/calibration_test.py  ->  writes analysis/calibration_report.md
"""
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

RESULTS = "model/results.csv"
OUT = "analysis/calibration_report.md"
MIN_TRAIN_DAYS = 7
MIN_STAT_N = 300          # fit per side x stat when the training set has this many rows
EDGES = [0.00, 0.03, 0.05]


def load():
    r = pd.read_csv(RESULTS)
    r = r[r.result.isin(["Win", "Loss"])].copy()
    r["win"] = (r.result == "Win").astype(int)
    r["pnl"] = np.where(r.win == 1, r.odds - 1, -1.0)          # 1 unit flat
    # no-vig fair probability from the best Over and best Under price at the same line
    k = ["date_melb", "player_key", "stat", "line"]
    piv = r.pivot_table(index=k, columns="side", values="odds", aggfunc="max")
    if {"Over", "Under"} <= set(piv.columns):
        piv = piv.dropna()
        io, iu = 1 / piv["Over"], 1 / piv["Under"]
        fair = pd.DataFrame({"fair_Over": io / (io + iu), "fair_Under": iu / (io + iu),
                             "overround": io + iu}).reset_index()
        r = r.merge(fair, on=k, how="left")
        r["fair"] = np.where(r.side == "Over", r.fair_Over, r.fair_Under)
    else:
        r["fair"], r["overround"] = np.nan, np.nan
    return r


def fit_predict(train, test):
    out = pd.Series(np.nan, index=test.index)
    for side in ["Over", "Under"]:
        tr_s, te_s = train[train.side == side], test[test.side == side]
        if len(tr_s) < 50 or te_s.empty:
            continue
        base = IsotonicRegression(out_of_bounds="clip", y_min=0.02, y_max=0.98).fit(tr_s.model_prob, tr_s.win)
        out[te_s.index] = base.predict(te_s.model_prob)
        for stat, te_st in te_s.groupby("stat"):
            tr_st = tr_s[tr_s.stat == stat]
            if len(tr_st) >= MIN_STAT_N:
                iso = IsotonicRegression(out_of_bounds="clip", y_min=0.02, y_max=0.98).fit(tr_st.model_prob, tr_st.win)
                out[te_st.index] = iso.predict(te_st.model_prob)
    return out


def summ(df, label):
    if df.empty:
        return f"| {label} | 0 | - | - | - |"
    return (f"| {label} | {len(df)} | {100*df.win.mean():.1f} | {df.pnl.sum():+.1f} | "
            f"{100*df.pnl.mean():+.1f} |")


def main():
    r = load()
    days = sorted(r.date_melb.unique())
    tests = []
    for i, d in enumerate(days):
        if i < MIN_TRAIN_DAYS:
            continue
        train, test = r[r.date_melb < d], r[r.date_melb == d].copy()
        test["cal"] = fit_predict(train, test)
        tests.append(test)
    t = pd.concat(tests)
    t = t[t.cal.notna()]
    oos_days = sorted(t.date_melb.unique())

    brier_raw = ((t.model_prob - t.win) ** 2).mean()
    brier_cal = ((t.cal - t.win) ** 2).mean()
    brier_mkt = ((t.implied - t.win) ** 2).mean()
    tf = t[t.fair.notna()]
    brier_fair = ((tf.fair - tf.win) ** 2).mean()

    L = [f"# Calibration-by-side test ({oos_days[0]} to {oos_days[-1]}, walk-forward)", "",
         f"Out-of-sample props: {len(t)} over {len(oos_days)} days; training window = all earlier days "
         f"(min {MIN_TRAIN_DAYS}). 1-unit flat stakes at the logged best price. "
         f"No-vig fair price available for {100*t.fair.notna().mean():.0f}% of rows "
         f"(median overround of best-price pairs {t.overround.median():.3f}).", "",
         "## Probability accuracy (Brier, lower = better)", "",
         "| Source | Brier |", "|---|---|",
         f"| Raw model prob | {brier_raw:.4f} |", f"| Calibrated (by side) | {brier_cal:.4f} |",
         f"| Implied 1/odds | {brier_mkt:.4f} |", f"| No-vig fair (rows with both sides) | {brier_fair:.4f} |", "",
         "## Selection rules, out of sample", "",
         "| Rule | n | Hit % | Units | ROI % |", "|---|---|---|---|---|",
         summ(t[t.tier.isin(["Diff 4", "Diff 3"]) & (t.side == "Over")], "Current: Diff 3+ Overs"),
         summ(t[t.tier.isin(["Diff 4", "Diff 3"])], "Current tiers, both sides")]
    for side in ["Over", "Under", "Both"]:
        s = t if side == "Both" else t[t.side == side]
        for e in EDGES:
            L.append(summ(s[s.cal > 1 / s.odds + e], f"{side}: calibrated > implied + {e:.2f}"))
        sf = s[s.fair.notna()]
        for e in EDGES:
            L.append(summ(sf[sf.cal > sf.fair + e], f"{side}: calibrated > no-vig fair + {e:.2f}"))
    L += ["", "## Reliability of calibrated probabilities (out of sample)", "",
          "| Side | Bucket | n | Mean calibrated | Actual hit |", "|---|---|---|---|---|"]
    t["b"] = pd.cut(t.cal, [0, .45, .5, .55, .6, .65, 1])
    for (side, b), g in t.groupby(["side", "b"], observed=True):
        L.append(f"| {side} | {b} | {len(g)} | {g.cal.mean():.3f} | {g.win.mean():.3f} |")
    L += ["", "## By day (best no-vig rule vs current)", "", "| Day | Current Diff3+ Overs units | Both: cal > fair + 0.03 units (n) |", "|---|---|---|"]
    for d, g in t.groupby("date_melb"):
        cur = g[g.tier.isin(["Diff 4", "Diff 3"]) & (g.side == "Over")]
        nv = g[g.fair.notna() & (g.cal > g.fair + 0.03)]
        L.append(f"| {d} | {cur.pnl.sum():+.1f} ({len(cur)}) | {nv.pnl.sum():+.1f} ({len(nv)}) |")
    L += ["", "Caveats: one season, 18 days; settled at best book including possibly stale one-book lines; "
          "best-price Over/Under pairs from different books understate the vig, so 'fair' is optimistic. "
          "Analysis only - no change to model.py, weights, thresholds or stakes."]
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
