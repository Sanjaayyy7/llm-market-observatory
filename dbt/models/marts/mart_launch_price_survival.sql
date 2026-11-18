-- Time at launch price for top-tier canonical models (Task 6 rulings 7-10).
with {{ exposure_ctes() }},

observed as (
    select canonical_model_id, listed_at, end_ts from exposure where is_top_tier
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
