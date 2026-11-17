-- G5 status seed: an in_scope row needs a non-empty api_id, a first-party provider and an https evidence_url
-- on the provider's doc_domain (or a subdomain), the crosswalk_manual_evidence rule.
with s as (
    select model_name, obs_date, provider, api_id, evidence_url,
        lower(regexp_extract(evidence_url, '^https://([^/:?#]+)', 1)) as host
    from {{ ref('seed_epoch_candidate_status') }}
    where scope = 'in_scope'
)

select model_name, obs_date, evidence_url
from s
where nullif(api_id, '') is null
    or not exists (select 1 from {{ ref('seed_provider_map') }} p where p.provider = s.provider and p.is_first_party)
    or not regexp_matches(coalesce(evidence_url, ''), '^https://')
    or not exists (
        select 1 from {{ ref('seed_provider_domains') }} d
        where d.provider = s.provider and (s.host = lower(d.doc_domain) or s.host like '%.' || lower(d.doc_domain))
    )
