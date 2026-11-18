-- Latest run only (R26). Upstream repeats rows: exact copies collapse, and a model whose rows disagree
-- is dropped rather than guessed (test epoch_crosswalked_model_conflicts fails if it is crosswalked).
with latest as (
    select distinct model, organization, publication_date, model_accessibility, open_model_weights
    from {{ source('raw', 'epoch') }}
    qualify run_date = max(run_date) over ()
)

select * from latest
qualify count(*) over (partition by model) = 1
