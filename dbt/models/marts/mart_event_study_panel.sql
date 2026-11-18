-- G8 descriptive event study panel (prereg docs/prereg/event-study.md §2-§3).
-- Series A: observed first cuts (LiteLLM date). Series B: the scored, non-data-fix subset at the provider's announced date.
-- Cuts within 28 days of a cluster's opening cut (inclusive, anchored, never chained) are one event.
with recursive groups as (
    select distinct provider, sdk_group from {{ ref('seed_provider_map') }} where sdk_group <> ''
),

series_a as (
    select 'A' as series, s.canonical_model_id, g.sdk_group,
           (s.first_cut_at at time zone 'UTC')::date as cut_date
    from {{ ref('mart_launch_price_survival') }} s
    join groups g on g.provider = s.provider
    where not s.censored
),

series_b as (
    select 'B' as series, a.canonical_model_id, a.sdk_group, c.announced_date as cut_date
    from series_a a
    join {{ ref('mart_cut_audit') }} c using (canonical_model_id)
    where c.is_scored_event and not c.is_data_fix
),

numbered as (
    select *, row_number() over (partition by series, sdk_group order by cut_date, canonical_model_id) as rn
    from (select * from series_a union all select * from series_b)
),

walk as (
    select series, sdk_group, rn, cut_date, cut_date as anchor from numbered where rn = 1
    union all
    select n.series, n.sdk_group, n.rn, n.cut_date,
           case when n.cut_date <= w.anchor + 28 then w.anchor else n.cut_date end
    from walk w
    join numbered n on n.series = w.series and n.sdk_group = w.sdk_group and n.rn = w.rn + 1
),

events as (
    select distinct series, sdk_group, anchor as event_date,
           series || ':' || sdk_group || ':' || strftime(anchor, '%Y-%m-%d') as event_id
    from walk
),

targets as (
    select series, event_id, event_date, sdk_group, sdk_group as target_group from events
    union all
    select series, event_id, event_date, sdk_group, 'control' from events where series = 'A'
),

raw_panel as (
    select t.series, t.event_id, t.event_date, f.sdk_group, r.rel_day, f.date, f.downloads
    from targets t
    cross join (select unnest(generate_series(-28, 28))::int as rel_day) r
    join {{ ref('fct_sdk_downloads_daily') }} f
        on f.sdk_group = t.target_group and f.date = t.event_date + r.rel_day
),

with_pre as (
    select *,
           count(*) filter (where rel_day < 0) over (partition by event_id, sdk_group) as n_pre,
           avg(downloads) filter (where rel_day < 0) over (partition by event_id, sdk_group) as pre_mean
    from raw_panel
)

select series, event_id, event_date, sdk_group, rel_day, date, downloads,
       case when n_pre = 28 and pre_mean > 0 then downloads / pre_mean end as norm
from with_pre
