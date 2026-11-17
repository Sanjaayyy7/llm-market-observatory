-- SCD2 per design §5. Snapshot universe = distinct (snapshot_date, commit_ts) in the input;
-- calendar gaps between snapshots are not absences (R31).
with universe as (
    select
        commit_ts,
        row_number() over (order by snapshot_date) as snap_no,
        lead(commit_ts) over (order by snapshot_date) as next_commit_ts
    from (select distinct snapshot_date, commit_ts from {{ ref('stg_litellm__snapshots') }})
),

numbered as (
    select s.model_key, s.commit_ts, s.in_per_mtok, s.out_per_mtok, u.snap_no, u.next_commit_ts
    from {{ ref('stg_litellm__snapshots') }} s
    join universe u on s.commit_ts = u.commit_ts
),

neighbours as (
    select
        *,
        lag(snap_no) over w as prev_snap_no,
        lag(in_per_mtok) over w as prev_in,
        lag(out_per_mtok) over w as prev_out,
        lead(snap_no) over w as next_snap_no
    from numbered
    window w as (partition by model_key order by snap_no)
),

-- int_price_versions: a change = first sight, return after absence, or a different price
int_price_versions as (
    select
        *,
        sum(case
            when prev_snap_no is null
              or prev_snap_no != snap_no - 1
              or in_per_mtok is distinct from prev_in
              or out_per_mtok is distinct from prev_out
            then 1 else 0 end) over (partition by model_key order by snap_no) as version_id,
        -- absent from the next snapshot of the universe (the latest snapshot has no next)
        next_commit_ts is not null and next_snap_no is distinct from snap_no + 1 as absent_next
    from neighbours
),

versions as (
    select
        model_key,
        min(commit_ts) as valid_from,
        max(in_per_mtok) as in_per_mtok,
        max(out_per_mtok) as out_per_mtok,
        bool_or(absent_next) as delisted,
        max(case when absent_next then next_commit_ts end) as absent_ts
    from int_price_versions
    group by model_key, version_id
)

select
    model_key,
    valid_from,
    case when delisted then absent_ts
         else lead(valid_from) over (partition by model_key order by valid_from) end as valid_to,
    in_per_mtok,
    out_per_mtok,
    delisted,
    valid_to is null as is_current
from versions
