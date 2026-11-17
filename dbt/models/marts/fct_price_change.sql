-- One row per change in a canonical model's blended price (Task 6 rulings 3, 5).
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

per_ts as (
    select canonical_model_id, valid_from as ts, min(blended) as blended
    from priced
    group by canonical_model_id, valid_from
),

seq as (
    select *, lag(blended) over (partition by canonical_model_id order by ts) as prev_blended
    from per_ts
),

-- consecutive equal prices collapse into one run; a run start is a change (or the listing)
runs as (select * from seq where prev_blended is null or blended != prev_blended),

listing as (select canonical_model_id, min(valid_from) as listed_at from priced group by canonical_model_id),

changes as (
    select r.canonical_model_id, r.ts as change_ts, r.prev_blended, r.blended,
        r.blended / r.prev_blended - 1 as pct, l.listed_at
    from runs r
    join listing l using (canonical_model_id)
    where r.prev_blended is not null
)

select
    c.canonical_model_id, c.change_ts, c.prev_blended, c.blended, c.pct,
    -- rounded so that exactly -10% is a cut despite float noise (0.9 - 1 = -0.0999...98)
    round(c.pct, 9) <= -0.10 as is_cut,
    -- spike rule: within 7 days of listing, or back at the old level within 14 days
    date_diff('day', c.listed_at, c.change_ts) <= 7
        or exists (
            select 1 from runs r
            where r.canonical_model_id = c.canonical_model_id
                and r.ts > c.change_ts and r.ts <= c.change_ts + interval 14 day
                and case when c.pct < 0 then r.blended >= c.prev_blended * 0.999
                         else r.blended <= c.prev_blended * 1.001 end
        ) as is_correction
from changes c
