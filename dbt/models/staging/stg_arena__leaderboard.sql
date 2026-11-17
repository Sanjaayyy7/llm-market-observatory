-- Latest run only (R26): each run is a full re-fetch.
with latest as (
    select * from {{ source('raw', 'arena') }} qualify run_date = max(run_date) over ()
)

select
    config,
    publish_date,
    model_name,
    category,
    rating,
    rank() over (partition by config, publish_date, category order by rating desc) as rank,
    rank() over (partition by config, publish_date, category order by rating desc)::double
        / count(*) over (partition by config, publish_date, category) as rank_percentile,
    nullif(license, '') = 'Proprietary' as closed
from latest
