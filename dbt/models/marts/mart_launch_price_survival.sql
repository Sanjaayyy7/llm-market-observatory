-- Time at launch price for top-tier canonical models (Task 6 rulings 7-10).
with run as (select max(commit_ts) as run_ts from {{ ref('stg_litellm__snapshots') }}),

keys as (
    -- first-party, non-alias LiteLLM keys per canonical model (Task 6 ruling 1)
    select distinct x.canonical_model_id, x.source_key as model_key
    from {{ ref('seed_model_crosswalk') }} x
    join (select distinct model_key, litellm_provider from {{ ref('stg_litellm__snapshots') }}) s
        on s.model_key = x.source_key
    join {{ ref('seed_provider_map') }} p on p.litellm_provider = s.litellm_provider and p.is_first_party
    where x.source = 'litellm' and not x.is_moving_alias
),

-- final delisting: no key has a current version; a temporary absence never censors
delist as (
    select k.canonical_model_id, max(v.valid_to) as delist_ts
    from {{ ref('dim_model_price') }} v
    join keys k using (model_key)
    group by k.canonical_model_id
    having count(*) filter (where v.is_current) = 0
),

-- S8: a provider-documented reroute retires the pinned model at the reroute date, or at the
-- target's first listing when the date is unknown
reroute as (
    select r.canonical_model_id, coalesce(r.reroute_date, t.listed_at::date)::timestamptz as censor_ts
    from {{ ref('seed_model_reroute') }} r
    left join {{ ref('mart_top_tier_screen') }} t on t.canonical_model_id = r.target_model_id
),

observed as (
    select
        s.canonical_model_id, s.listed_at,
        least(coalesce(rr.censor_ts, run.run_ts), coalesce(d.delist_ts, run.run_ts), run.run_ts) as end_ts
    from {{ ref('mart_top_tier_screen') }} s
    cross join run
    left join delist d using (canonical_model_id)
    left join reroute rr using (canonical_model_id)
    where s.is_top_tier
),

first_cut as (
    select o.canonical_model_id, min(c.change_ts) as first_cut_at, arg_min(-c.pct, c.change_ts) as cut_depth_pct
    from observed o
    join {{ ref('fct_price_change') }} c
        on c.canonical_model_id = o.canonical_model_id
        and c.is_cut and not c.is_correction and c.change_ts < o.end_ts
    group by o.canonical_model_id
)

select
    o.canonical_model_id,
    m.provider,
    o.listed_at,
    f.first_cut_at,
    date_diff('day', o.listed_at::date, coalesce(f.first_cut_at, o.end_ts)::date) as days_at_launch_price,
    f.first_cut_at is null as censored,
    f.cut_depth_pct
from observed o
join {{ ref('dim_model') }} m using (canonical_model_id)
left join first_cut f using (canonical_model_id)
