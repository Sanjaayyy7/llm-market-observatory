import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ingest.draft_crosswalk import (
    build,
    canon,
    draft,
    is_moving_alias,
    match_score,
    write_seeds,
)


def test_alias_dated_twin():
    assert is_moving_alias("gpt-4o", {"gpt-4o", "gpt-4o-2024-08-06"})


def test_stable_undated_not_alias():
    assert not is_moving_alias("gpt-5.4", {"gpt-5.4"})


def test_twin_requires_whole_date_suffix():
    assert not is_moving_alias("claude-opus-4", {"claude-opus-4", "claude-opus-4-1-20250805"})


def test_latest_is_alias():
    assert is_moving_alias("gemini-pro-latest", set())


def test_manual_alias_list():
    assert is_moving_alias("deepseek-chat", set())


def test_canon_collapses_variants():
    assert canon("Claude Opus 5.5 (High)") == "claude-opus-5-5"
    assert canon("claude-opus-5.5-thinking") == "claude-opus-5-5"


def test_canon_keeps_dated_parens():
    assert canon("Gemini 2.5 Pro (03-25)") == "gemini-2-5-pro-03-25"
    assert canon("Gemini 2.5 Pro (03-25)") != canon("Gemini 2.5 Pro (05-06)")


def test_canon_strips_effort_suffix():
    assert canon("o3-mini-high") == "o3-mini"
    assert canon("claude-opus-4-5-20251101-high-32k") == "claude-opus-4-5-20251101"
    assert canon("qwen3-235b-a22b-no-thinking") == "qwen3-235b-a22b"
    assert canon("qwen3-max") == "qwen3-max"


def test_match_score_uses_raw_name():
    assert match_score("Claude Opus 5.5 (High)", "claude-opus-5-5") < 1.0
    assert match_score("claude-opus-5-5", "claude-opus-5-5") == 1.0


PROVIDER_MAP = pd.DataFrame({
    "litellm_provider": ["openai", "vertex_ai-language-models", "mistral"],
    "provider": ["openai", "google", "mistral"],
    "is_first_party": [True, False, True],
})


def _inputs():
    arena = pd.DataFrame([
        ("GPT 5 (High)", "openai", date(2026, 1, 1), 0.1, True),
        ("gpt-5", "openai", date(2026, 1, 1), 0.2, True),
        ("Unlisted Model", "openai", date(2026, 1, 1), 0.05, True),
        ("Other Thing", "someorg", date(2026, 1, 1), 0.05, False),
    ], columns=["model_name", "organization", "publish_date", "rank_percentile", "closed"])
    litellm = pd.DataFrame([
        ("gpt-5", "openai", pd.Timestamp("2025-12-01", tz="UTC")),
        ("vertex_ai/gpt-5", "vertex_ai-language-models", pd.Timestamp("2025-12-01", tz="UTC")),
    ], columns=["model_key", "litellm_provider", "first_ts"])
    epoch = pd.DataFrame({"model": ["GPT-5"]})
    return arena, litellm, epoch, PROVIDER_MAP


def test_draft_scores_every_row():
    _, xwalk = draft(*_inputs())
    assert len(xwalk) == 4  # 2 arena + 1 litellm + 1 epoch; vertex key and out-of-scope names excluded
    assert xwalk["match_score"].notna().all()
    assert set(xwalk["canonical_model_id"]) == {"gpt-5"}
    by_key = xwalk.set_index(["source", "source_key"])["match_method"]
    assert by_key[("arena", "gpt-5")] == "exact"
    assert by_key[("arena", "GPT 5 (High)")] == "manual"
    assert xwalk["approved_by"].isna().all() or (xwalk["approved_by"] == "").all()


def test_draft_models_row():
    models, _ = draft(*_inputs())
    row = models.iloc[0]
    assert (row["canonical_model_id"], row["provider"], row["display_name"]) == ("gpt-5", "openai", "GPT 5 (High)")
    assert row["open_weights"] is not None and not row["open_weights"]


def test_draft_refuses_to_clobber_filled_seed(tmp_path):
    models, xwalk = draft(*_inputs())
    path = tmp_path / "seed_model_crosswalk.csv"
    path.write_text("source,source_key,canonical_model_id,evidence_url,approved_by\narena,x,y,https://a.b/c,\n")
    before = path.read_text()
    with pytest.raises(ValueError):
        write_seeds(tmp_path, models, xwalk)
    assert path.read_text() == before
    assert not (tmp_path / "seed_models.csv").exists()


def test_write_seeds_writes_when_unfilled(tmp_path):
    models, xwalk = draft(*_inputs())
    write_seeds(tmp_path, models, xwalk)
    write_seeds(tmp_path, models, xwalk)  # re-draft over an unfilled seed is allowed
    assert (tmp_path / "seed_models.csv").read_text().startswith("canonical_model_id,provider,")


def _alias_inputs(keys, arena_name, provider="openai"):
    ts = pd.Timestamp("2025-01-01", tz="UTC")
    litellm = pd.DataFrame([(k, provider, ts) for k in keys],
                           columns=["model_key", "litellm_provider", "first_ts"])
    arena = pd.DataFrame([(arena_name, provider, date(2025, 2, 1), 0.1, True)],
                         columns=["model_name", "organization", "publish_date", "rank_percentile", "closed"])
    return arena, litellm, pd.DataFrame({"model": []}), PROVIDER_MAP


def test_arena_alias_repoints_to_single_dated_twin():
    models, xwalk = draft(*_alias_inputs(["gpt-5.1", "gpt-5.1-2025-11-13"], "GPT-5.1"))
    row = xwalk[xwalk["source"] == "arena"].iloc[0]
    assert (row["canonical_model_id"], row["match_method"]) == ("gpt-5.1-2025-11-13", "manual")
    assert not row["is_moving_alias"]
    assert row["match_score"] == match_score("GPT-5.1", "gpt-5.1-2025-11-13")
    lit = xwalk[xwalk["source"] == "litellm"].set_index("source_key")
    assert lit.loc["gpt-5.1", "is_moving_alias"] and lit.loc["gpt-5.1", "canonical_model_id"] == "gpt-5.1"
    assert lit.loc["gpt-5.1-2025-11-13", "canonical_model_id"] == "gpt-5.1-2025-11-13"
    assert set(models["canonical_model_id"]) == {"gpt-5.1", "gpt-5.1-2025-11-13"}


def test_multi_twin_alias_not_repointed():
    built = build(*_alias_inputs(["mistral-medium", "mistral-medium-2312", "mistral-medium-2505"],
                                 "mistral-medium", provider="mistral"))
    xwalk = built["xwalk"]
    row = xwalk[xwalk["source"] == "arena"].iloc[0]
    assert row["canonical_model_id"] == "mistral-medium" and row["is_moving_alias"]
    assert any(n.startswith("MULTI_TWIN mistral: mistral-medium -> mistral-medium twins=") for n in built["notes"])
