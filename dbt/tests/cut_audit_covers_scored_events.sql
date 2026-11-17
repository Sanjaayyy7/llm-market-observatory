{{ config(enabled = target.name != 'ci') }}
-- G4 council: every scored event (a top-tier first cut before censoring) joins exactly one audit
-- row with a verdict, so the kill-rate frame cannot silently shrink.
select s.canonical_model_id, s.first_cut_at, count(a.canonical_model_id) as n_audit
from {{ ref('mart_launch_price_survival') }} s
left join {{ ref('mart_cut_audit') }} a
    on a.canonical_model_id = s.canonical_model_id
    and a.observed_ts = s.first_cut_at
    and a.verdict is not null
where s.first_cut_at is not null
group by s.canonical_model_id, s.first_cut_at
having count(a.canonical_model_id) != 1
