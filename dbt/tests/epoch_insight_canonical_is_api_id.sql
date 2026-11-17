-- G5: every epoch_insight crosswalk row's canonical_model_id equals the status seed's api_id for the same model_name|obs_date.
select x.source_key, x.canonical_model_id, s.api_id
from {{ ref('seed_model_crosswalk') }} x
left join {{ ref('seed_epoch_candidate_status') }} s on x.source_key = s.model_name || '|' || s.obs_date
where x.source = 'epoch_insight' and x.canonical_model_id is distinct from s.api_id
