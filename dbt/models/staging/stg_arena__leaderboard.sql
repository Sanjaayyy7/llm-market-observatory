-- Latest run only (R26): each run is a full re-fetch.
with latest as (
    select * from {{ source('raw', 'arena') }} qualify run_date = max(run_date) over ()
),

ranked as (
    select
        *,
        rank() over (partition by config, publish_date, category order by rating desc) as rank,
        count(*) over (partition by config, publish_date, category) as n_in_category
    from latest
)

select
    config,
    publish_date,
    model_name,
    category,
    rating,
    rank,
    rank::double / n_in_category as rank_percentile,
    nullif(license, '') = 'Proprietary' as closed
from ranked
