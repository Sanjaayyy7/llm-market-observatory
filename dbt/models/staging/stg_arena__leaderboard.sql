-- Latest run only: each run is a full re-fetch (R26). qualify, not a scalar subquery: that
-- returned 0 rows on single-partition fixtures (DuckDB 1.5.6).
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
