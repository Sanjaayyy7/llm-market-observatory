-- design §18 G4: audit at least least(20, real cuts) rows.
select n_audited, n_cuts
from (
    select
        (select count(*) from {{ ref('seed_cut_audit') }}) as n_audited,
        (select count(*) from {{ ref('fct_price_change') }} where is_cut and not is_correction) as n_cuts
)
where n_audited < least(20, n_cuts)
