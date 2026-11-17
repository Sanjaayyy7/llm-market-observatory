{{ config(enabled = target.name != 'ci', severity = 'warn') }}
-- PRD M1 / design §6: below 90% → headline restricted to the mapped set + coverage disclosed
-- (DECISIONS 2026-11-17 council); not a kill.
select n_scope, n_covered, n_covered::double / n_scope as share
from (
    select count(*) as n_scope, count(*) filter (where covered) as n_covered
    from {{ ref('int_crosswalk_coverage') }}
)
where n_covered::double / n_scope < 0.90
