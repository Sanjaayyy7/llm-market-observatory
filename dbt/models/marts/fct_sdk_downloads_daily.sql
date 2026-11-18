-- Daily PyPI downloads per SDK group, zero-filled (prereg docs/prereg/event-study.md §1).
-- A missing day is 0: ClickPy's summing table has no row for a zero day. A group's coverage runs from
-- its earliest member's first date to the data's last date.
with member_days as (
    select s.sdk_group, d.date, sum(d.downloads) as downloads
    from {{ ref('stg_pypi__downloads') }} d
    join {{ ref('seed_sdk_packages') }} s on d.project = s.package
    group by s.sdk_group, d.date
),

coverage as (
    select sdk_group, min(date) as first_date, (select max(date) from {{ ref('stg_pypi__downloads') }}) as last_date
    from member_days
    group by sdk_group
),

spine as (
    select sdk_group, unnest(generate_series(first_date::date, last_date::date, interval 1 day))::date as date
    from coverage
)

select sp.sdk_group, sp.date, coalesce(m.downloads, 0) as downloads
from spine sp
left join member_days m on m.sdk_group = sp.sdk_group and m.date = sp.date
