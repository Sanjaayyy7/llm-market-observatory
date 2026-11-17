-- design §5: exactly one is_current row per non-delisted key (none per delisted key),
-- and valid_from < valid_to on every row.
with per_key as (
    select
        model_key,
        count(*) filter (where is_current) as n_current,
        arg_max(delisted, valid_from) as last_delisted
    from {{ ref('dim_model_price') }}
    group by model_key
)
select model_key, 'bad is_current count' as problem
from per_key
where n_current != case when last_delisted then 0 else 1 end
union all
select model_key, 'valid_from >= valid_to'
from {{ ref('dim_model_price') }}
where valid_from >= valid_to
