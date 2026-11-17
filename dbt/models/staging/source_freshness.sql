-- sla_days = ceil(p90 gap between consecutive distinct data dates): the measured cadence.
with data_dates(source, data_date) as (
    select 'litellm', snapshot_date from {{ ref('stg_litellm__snapshots') }}
    union select 'arena', publish_date from {{ ref('stg_arena__leaderboard') }}
    union select 'epoch', publication_date from {{ ref('stg_epoch__models') }}
    union select 'pypi', date from {{ ref('stg_pypi__downloads') }}
    union select 'tokencanopy', run_date from {{ ref('stg_tokencanopy__prices') }}
),
gaps as (
    select source, data_date - lag(data_date) over (partition by source order by data_date) as gap
    from (select distinct source, data_date from data_dates)
),
sla as (
    select source, ceil(quantile_cont(gap, 0.9))::int as sla_days   -- null with < 2 dates
    from gaps group by source
),
latest as (
    select * from {{ source('raw', 'freshness') }} where not probe
    qualify row_number() over (partition by source order by run_ts desc) = 1
)

select
    l.source,
    l.run_ts,
    l.rows,
    l.max_date,
    s.sla_days,
    -- +1 = publication day; anchored to the run, not current_date
    cast(l.run_ts at time zone 'UTC' as date) - l.max_date > coalesce(s.sla_days, 0) + 1 as is_stale
from latest l
left join sla s using (source)
