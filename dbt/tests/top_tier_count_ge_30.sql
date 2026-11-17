{{ config(enabled = target.name != 'ci') }}
-- design §18 G2 kill criterion: fewer than 30 top-tier canonical models.
select n_top_tier
from (select count(*) filter (where is_top_tier) as n_top_tier from {{ ref('mart_top_tier_screen') }})
where n_top_tier < 30
