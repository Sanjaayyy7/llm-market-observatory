-- Mode scope is per row (design §5 v1.2.1), so a key that is ever out of scope would look
-- delisted. Fails for any key mapped to a top-tier canonical model with a raw row whose non-null
-- mode is outside chat/completion/responses. This also covers a key that entered scope after
-- first appearing out of scope. If it fails, take the left_scope split to a mini-council.
select
    x.canonical_model_id, r.model_key, r.mode,
    min(r.snapshot_date) as first_out_of_scope, max(r.snapshot_date) as last_out_of_scope
from {{ source('raw', 'litellm') }} r
join {{ ref('seed_model_crosswalk') }} x on x.source = 'litellm' and x.source_key = r.model_key
join {{ ref('mart_top_tier_screen') }} t on t.canonical_model_id = x.canonical_model_id and t.is_top_tier
where r.mode is not null and r.mode not in ('chat', 'completion', 'responses')
group by x.canonical_model_id, r.model_key, r.mode
