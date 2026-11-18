{% macro exposure_ctes() %}
{#- Exposure window per priced canonical model (Task 6 rulings 7-10, S8): CTEs run, keys, delist,
    reroute, exposure. A macro, not a model, so the refs stay direct inputs of every caller
    and the mart's unit tests keep mocking the same inputs. -#}
run as (select max(commit_ts) as run_ts from {{ ref('stg_litellm__snapshots') }}),

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

exposure as (
    select
        s.canonical_model_id, s.listed_at, s.is_top_tier,
        least(coalesce(rr.censor_ts, run.run_ts), coalesce(d.delist_ts, run.run_ts), run.run_ts) as end_ts
    from {{ ref('mart_top_tier_screen') }} s
    cross join run
    left join delist d using (canonical_model_id)
    left join reroute rr using (canonical_model_id)
    where s.listed_at is not null
)
{% endmacro %}
