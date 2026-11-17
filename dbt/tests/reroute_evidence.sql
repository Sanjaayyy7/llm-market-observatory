-- S8: every reroute row needs an https evidence_url on the provider's doc domain (or a
-- subdomain), an approver, and both model IDs in seed_models.
with rows as (
    select
        r.canonical_model_id, r.target_model_id, r.evidence_url, r.approved_by,
        lower(regexp_extract(r.evidence_url, '^https://([^/:?#]+)', 1)) as host,
        m.provider
    from (
        select canonical_model_id, target_model_id, evidence_url, approved_by from {{ ref('seed_model_reroute') }}
        union all
        -- G4: documented temporary prices follow the same evidence rule
        select canonical_model_id, canonical_model_id, evidence_url, approved_by from {{ ref('seed_temporary_price') }}
    ) r
    left join {{ ref('seed_models') }} m on m.canonical_model_id = r.canonical_model_id
)

select canonical_model_id, target_model_id, evidence_url
from rows
where nullif(approved_by, '') is null
    or evidence_url is null
    or not regexp_matches(evidence_url, '^https://')
    or provider is null
    or not exists (select 1 from {{ ref('seed_models') }} t where t.canonical_model_id = rows.target_model_id)
    or not exists (
        select 1 from {{ ref('seed_provider_domains') }} d
        where d.provider = rows.provider
            and (rows.host = lower(d.doc_domain) or rows.host like '%.' || lower(d.doc_domain))
    )
