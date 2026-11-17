-- One row per canonical model in the key set. Top tier = Arena text/overall rank percentile
-- <= 25% on the first snapshot within 60 days after listing; unranked ones are excluded from
-- survival and counted (PRD §6).
with keys as (
    -- first-party, non-alias LiteLLM keys per canonical model (Task 6 ruling 1)
    select distinct x.canonical_model_id, x.source_key as model_key
    from {{ ref('seed_model_crosswalk') }} x
    join (select distinct model_key, litellm_provider from {{ ref('stg_litellm__snapshots') }}) s
        on s.model_key = x.source_key
    join {{ ref('seed_provider_map') }} p on p.litellm_provider = s.litellm_provider and p.is_first_party
    where x.source = 'litellm' and not x.is_moving_alias
),

priced as (
    -- null or non-positive blended versions are dropped before listing and change detection
    select k.canonical_model_id, v.valid_from, v.valid_to, round((3 * v.in_per_mtok + v.out_per_mtok) / 4, 6) as blended
    from {{ ref('dim_model_price') }} v
    join keys k using (model_key)
    where round((3 * v.in_per_mtok + v.out_per_mtok) / 4, 6) > 0
),

listing as (select canonical_model_id, min(valid_from) as listed_at from priced group by canonical_model_id),

first_rank as (
    select l.canonical_model_id, arg_min(r.rank_percentile, r.publish_date) as first_rank_pct
    from listing l
    join {{ ref('fct_arena_rank') }} r
        on r.canonical_model_id = l.canonical_model_id
        and r.publish_date between l.listed_at::date and l.listed_at::date + 60
    group by l.canonical_model_id
)

select
    l.canonical_model_id,
    l.listed_at,
    f.first_rank_pct,
    coalesce(f.first_rank_pct <= 0.25, false) as is_top_tier,
    f.first_rank_pct is null as is_unranked
from listing l
left join first_rank f using (canonical_model_id)
