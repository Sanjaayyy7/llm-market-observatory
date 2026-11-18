import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.event_study import (
    FROZEN_EVENTS,
    after_prereg,
    event_windows,
    matches_prereg,
    placebo_ratios,
    to_strict_json,
    verdict_line,
)

START = pd.Timestamp("2024-01-01")


def daily(group, n_days, excluded_around=(), value=lambda i: 100 + i):
    dates = pd.date_range(START, periods=n_days)
    excl = [any(abs((d - pd.Timestamp(e)).days) <= 28 for e in excluded_around) for d in dates]
    return pd.DataFrame({"sdk_group": group, "date": dates, "downloads": [value(i) for i in range(n_days)],
                         "excluded": excl})


def panel(rel_days, pre=100.0, post=200.0, event_id="A:openai:2024-03-01"):
    rows = [{"series": "A", "event_id": event_id, "event_date": "2024-03-01", "sdk_group": "openai",
             "rel_day": r, "date": "2024-03-01", "downloads": pre if r < 0 else post, "norm": 1.0}
            for r in rel_days]
    return pd.DataFrame(rows)


def test_placebo_seeded_deterministic():
    df = pd.concat([daily("openai", 400), daily("anthropic", 400)], ignore_index=True)
    a, b = placebo_ratios(df), placebo_ratios(df)
    pd.testing.assert_frame_equal(a, b)
    by = {g: sorted(x["pseudo_date"]) for g, x in a.groupby("sdk_group")}
    assert len(by["openai"]) == 100 and by["openai"] != by["anthropic"]


def test_placebo_excludes_near_event_and_needs_full_window():
    df = daily("openai", 300, excluded_around=["2024-05-01"])
    out = placebo_ratios(df, n=10_000)
    got = set(pd.to_datetime(out["pseudo_date"]))
    first, last = START + pd.Timedelta(days=28), START + pd.Timedelta(days=299 - 27)
    want = {d for d, ex in zip(df["date"], df["excluded"], strict=True) if not ex and first <= d <= last}
    assert got == want and len(got) == len(out)


def test_placebo_skips_control_and_caps_n():
    df = pd.concat([daily("requests", 200), daily("mistral", 200)], ignore_index=True)
    out = placebo_ratios(df, n=5)
    assert set(out["sdk_group"]) == {"mistral"} and len(out) == 5


def test_event_windows_ratio_and_incomplete_flag():
    full = event_windows(panel(range(-28, 29)))
    r = full.iloc[0]
    assert r["ratio"] == pytest.approx(2.0) and not r["incomplete_window"]
    assert (r["n_pre"], r["n_post"]) == (28, 28)
    short = event_windows(panel(range(-28, 20))).iloc[0]
    assert short["ratio"] is None and short["incomplete_window"] and short["n_post"] == 20
    zero = event_windows(panel(range(-28, 29), pre=0.0)).iloc[0]
    assert zero["ratio"] is None and zero["incomplete_window"]


def test_verdict_line_below_and_at_floor():
    assert verdict_line(6) == "Descriptive only: n=6 events, below the pre-registered floor of 8."
    assert verdict_line(7).endswith("below the pre-registered floor of 8.")
    assert verdict_line(8) == "Descriptive only: n=8 events; inference not built in v1.0."


def test_matches_prereg_detects_extra_cut():
    assert len(FROZEN_EVENTS) == 9
    assert matches_prereg(list(FROZEN_EVENTS))
    assert not matches_prereg([*FROZEN_EVENTS, ("new-model", "openai", "2026-11-10", None)])
    assert not matches_prereg(list(FROZEN_EVENTS)[:-1])


def test_json_is_strict():
    def boom(c):
        raise ValueError(c)

    text = to_strict_json({"a": float("nan"), "b": np.float64("nan"), "c": [1.5, None], "d": np.int64(3)})
    assert json.loads(text, parse_constant=boom) == {"a": None, "b": None, "c": [1.5, None], "d": 3}


def test_placebo_share_is_none_without_a_ratio():
    # G8 co-founder review: an incomplete window's ratio arrives as NaN and must not score 0.0
    from analysis.event_study import placebo_share
    pool = pd.Series([0.5, 1.5])
    assert placebo_share(None, pool) is None
    assert placebo_share(float("nan"), pool) is None
    assert placebo_share(1.0, pd.Series([], dtype=float)) is None
    assert placebo_share(1.0, pool) == 0.5


def test_after_prereg_labels_only_events_with_a_new_cut():
    frozen = list(FROZEN_EVENTS)
    new = ("new-model", "openai", "2026-11-10", None)
    assert not after_prereg([frozen[0][0]], frozen)
    assert after_prereg(["new-model"], [*frozen, new])
    assert not after_prereg([frozen[0][0]], [*frozen, new])
    assert after_prereg(["mistral-large-2402"], [("mistral-large-2402", "mistral", "2024-06-01", None)])
