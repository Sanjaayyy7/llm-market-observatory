-- Approval requires evidence (design §6): an approved manual row needs an https URL on the
-- provider's doc domain (or a subdomain) and a match_score. Draft rows (approved_by null) pass.
with manual as (
    select
        x.source, x.source_key, x.evidence_url, x.match_score,
        lower(regexp_extract(x.evidence_url, '^https://([^/:?#]+)', 1)) as host,
        m.provider
    from {{ ref('seed_model_crosswalk') }} x
    left join {{ ref('seed_models') }} m using (canonical_model_id)
    where x.match_method = 'manual' and nullif(x.approved_by, '') is not null
)

select source, source_key, evidence_url
from manual
where evidence_url is null
    or not regexp_matches(evidence_url, '^https://')
    or match_score is null
    or not exists (
        select 1 from {{ ref('seed_provider_domains') }} d
        where d.provider = manual.provider
            and (manual.host = lower(d.doc_domain) or manual.host like '%.' || lower(d.doc_domain))
    )
