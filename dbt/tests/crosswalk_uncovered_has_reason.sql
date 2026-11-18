{{ config(enabled = target.name != 'ci') }}
-- G2 council deferral: every uncovered in-scope name has a reason row, and no reason row is stale.
select c.model_name, 'uncovered name has no seed row' as problem
from {{ ref('int_crosswalk_coverage') }} c
left join {{ ref('seed_crosswalk_uncovered') }} s using (model_name)
where not c.covered and s.model_name is null
union all
select s.model_name, 'seed row is not an uncovered name today' as problem
from {{ ref('seed_crosswalk_uncovered') }} s
left join {{ ref('int_crosswalk_coverage') }} c on c.model_name = s.model_name and not c.covered
where c.model_name is null
