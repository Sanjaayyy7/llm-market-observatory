-- Latest run only (R26).
select model, organization, publication_date, model_accessibility, open_model_weights
from {{ source('raw', 'epoch') }}
qualify run_date = max(run_date) over ()
