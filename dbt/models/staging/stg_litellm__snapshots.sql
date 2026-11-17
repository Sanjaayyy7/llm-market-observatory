-- Design §5 step 1 + R32: fill a null mode from the key's next non-null mode (else previous),
-- then filter. A key never given a mode is kept.
with filled as (
    select
        *,
        coalesce(
            mode,
            first_value(mode ignore nulls) over (
                partition by model_key order by snapshot_date
                rows between current row and unbounded following),
            last_value(mode ignore nulls) over (
                partition by model_key order by snapshot_date
                rows between unbounded preceding and current row)
        ) as mode_filled
    from {{ source('raw', 'litellm') }}
)

select
    snapshot_date,
    commit_sha,
    commit_ts,
    model_key,
    litellm_provider,
    mode_filled as mode,
    round(input_cost_per_token * 1e6, 6) as in_per_mtok,
    round(output_cost_per_token * 1e6, 6) as out_per_mtok
from filled
where mode_filled in ('chat', 'completion', 'responses') or mode_filled is null
