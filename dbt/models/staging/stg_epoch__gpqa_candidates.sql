-- G5 candidates: Epoch's GPQA Diamond rows against the GPT-4-0314 threshold, from both frozen insight seeds.
-- Key is (model_name, obs_date): "Command R+" appears twice.
select "Model Name" as model_name, "Release Date" as obs_date, "USD per 1M Tokens" as usd_per_mtok,
    benchmark_score as gpqa_score, true as is_frontier
from {{ ref('seed_epoch_insight_frontier') }}
where bench = 'GPQA Diamond' and threshold_model = 'GPT-4-0314'
union all
select "Model Name", "Release Date", "USD per 1M Tokens", benchmark_score, false
from {{ ref('seed_epoch_insight_other') }}
where bench = 'GPQA Diamond' and threshold_model = 'GPT-4-0314'
