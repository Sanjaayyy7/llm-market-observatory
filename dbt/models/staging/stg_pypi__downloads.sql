-- Latest run only (R26).
with latest as (
    select * from {{ source('raw', 'pypi') }} qualify run_date = max(run_date) over ()
)
-- ClickPy stores a SummingMergeTree: duplicate (date, project) rows are partial sums (R27).
select date, project, sum(count) as downloads
from latest
group by date, project
