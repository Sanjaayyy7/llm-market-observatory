-- design §5: exactly one is_current row per non-delisted key (none per delisted key).
with per_key as (
    select
        model_key,
        count(*) filter (where is_current) as n_current,
        arg_max(delisted, valid_from) as last_delisted
    from {{ ref('dim_model_price') }}
    group by model_key
)
select model_key
from per_key
where n_current != case when last_delisted then 0 else 1 end
