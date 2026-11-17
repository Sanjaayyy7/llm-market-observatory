{{ config(enabled = target.name != 'ci') }}
-- Every audit row must match a real cut, cite a provider-domain https URL (subdomains OK) and quote the page.
with audit as (
    select
        a.canonical_model_id, a.observed_ts, a.source_url, a.evidence_quote,
        lower(regexp_extract(a.source_url, '^https://([^/:?#]+)', 1)) as host,
        m.provider
    from {{ ref('seed_cut_audit') }} a
    left join {{ ref('seed_models') }} m using (canonical_model_id)
)

select canonical_model_id, observed_ts, source_url
from audit
where nullif(trim(evidence_quote), '') is null
    or not regexp_matches(source_url, '^https://')
    or not exists (
        select 1 from {{ ref('seed_provider_domains') }} d
        where d.provider = audit.provider
            and (audit.host = lower(d.doc_domain) or audit.host like '%.' || lower(d.doc_domain))
    )
    or not exists (
        select 1 from {{ ref('fct_price_change') }} c
        where c.canonical_model_id = audit.canonical_model_id and c.change_ts = audit.observed_ts
            and c.is_cut and not c.is_correction
    )
