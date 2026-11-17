{{ config(severity = 'warn') }}
-- Keys of one canonical model must agree on every snapshot day (Task 6 ruling 3): the mart
-- takes min(blended) and counts one change per canonical, which is only right if they agree.
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

days as (select distinct snapshot_date as date from {{ ref('stg_litellm__snapshots') }})

select p.canonical_model_id, d.date, min(p.blended) as min_blended, max(p.blended) as max_blended
from priced p
join days d on p.valid_from::date <= d.date and (p.valid_to is null or p.valid_to::date > d.date)
group by p.canonical_model_id, d.date
having min(p.blended) != max(p.blended)
