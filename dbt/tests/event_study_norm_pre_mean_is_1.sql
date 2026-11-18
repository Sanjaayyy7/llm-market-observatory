-- Over the pre window norm averages exactly 1, wherever it is defined.
select event_id, sdk_group, avg(norm) as pre_norm_mean
from {{ ref('mart_event_study_panel') }}
where rel_day < 0
group by event_id, sdk_group
having count(*) = 28 and avg(downloads) > 0 and abs(avg(norm) - 1) >= 1e-9
