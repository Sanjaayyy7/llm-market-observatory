{{ config(enabled = target.name != 'ci') }}
-- design §18 G2 kill criterion: fewer than 80% of in-scope closed models covered.
select n_closed, n_closed_covered, n_closed_covered::double / n_closed as closed_share
from (
    select count(*) as n_closed, count(*) filter (where covered) as n_closed_covered
    from {{ ref('int_crosswalk_coverage') }}
    where closed is true
)
where n_closed_covered::double / n_closed < 0.80
