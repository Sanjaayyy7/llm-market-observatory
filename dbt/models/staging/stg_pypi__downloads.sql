-- Latest run only (R26). qualify, not a scalar subquery: that returned 0 rows on
-- single-partition fixtures (DuckDB 1.5.6).
with latest as (
    select * from {{ source('raw', 'pypi') }} qualify run_date = max(run_date) over ()
)
-- ClickPy stores a SummingMergeTree: duplicate (date, project) rows are partial sums (R27).
select date, project, sum(count) as downloads
from latest
group by date, project
