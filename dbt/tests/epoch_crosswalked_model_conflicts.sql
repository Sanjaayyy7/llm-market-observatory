-- stg_epoch__models drops a model whose latest-run rows disagree; a crosswalked one would silently
-- leave listing_lag, so it must fail the build instead (2026-11-18: Magistral Medium 1.1 had two dates).
select model
from (
    select distinct model, organization, publication_date, model_accessibility, open_model_weights
    from {{ source('raw', 'epoch') }}
    qualify run_date = max(run_date) over ()
)
where model in (select source_key from {{ ref('seed_model_crosswalk') }} where source = 'epoch')
group by model
having count(*) > 1
