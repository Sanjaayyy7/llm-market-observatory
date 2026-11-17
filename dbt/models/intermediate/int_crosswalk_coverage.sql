-- One row per in-scope Arena name. In-scope = first-party names that reached the top 25% on any
-- text/overall snapshot. Covered = has an arena crosswalk row whose canonical model has a litellm row.
with org as (
    select model_name, lower(max(nullif(organization, ''))) as organization
    from {{ source('raw', 'arena') }}
    where config = 'text' and category = 'overall'
        and run_date = (select max(run_date) from {{ source('raw', 'arena') }})
    group by 1
),

names as (
    select
        s.model_name,
        bool_or(s.closed) as closed,
        min(s.rank_percentile) as min_pct,
        coalesce(max(case when o.organization = 'alibaba' then 'qwen' else o.organization end), '') as provider
    from {{ ref('stg_arena__leaderboard') }} s
    left join org o using (model_name)
    where s.config = 'text' and s.category = 'overall'
    group by 1
),

scope as (
    select n.model_name, n.closed, n.provider
    from names n
    join {{ ref('seed_provider_map') }} p on p.provider = n.provider and p.is_first_party
    where n.min_pct <= 0.25
    group by 1, 2, 3
),

flagged as (
    select
        s.model_name, s.closed, s.provider,
        exists (
            select 1
            from {{ ref('seed_model_crosswalk') }} a
            join {{ ref('seed_model_crosswalk') }} l
                on l.canonical_model_id = a.canonical_model_id and l.source = 'litellm'
            where a.source = 'arena' and a.source_key = s.model_name
        ) as covered
    from scope s
)

select model_name, provider, closed, covered from flagged
