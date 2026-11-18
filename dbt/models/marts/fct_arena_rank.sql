-- Best-variant Arena rank per canonical model and snapshot (design §6). The percentile
-- denominator stays every Arena row of the snapshot (computed in staging).
select
    x.canonical_model_id,
    s.publish_date,
    min(s.rank) as rank,
    min(s.rank_percentile) as rank_percentile,
    case
        when s.publish_date < date '2024-01-09' then 1
        when s.publish_date < date '2025-05-16' then 2
        when s.publish_date < date '2025-07-23' then 3
        else 4
    end as method_era
from {{ ref('stg_arena__leaderboard') }} s
join {{ ref('seed_model_crosswalk') }} x on x.source = 'arena' and x.source_key = s.model_name
where s.config = 'text' and s.category = 'overall'
group by x.canonical_model_id, s.publish_date
