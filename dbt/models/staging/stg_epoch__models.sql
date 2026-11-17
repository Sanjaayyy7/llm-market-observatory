-- Latest run only (R26). qualify, not a scalar subquery: that returned 0 rows on
-- single-partition fixtures (DuckDB 1.5.6).
select model, organization, publication_date, model_accessibility, open_model_weights
from {{ source('raw', 'epoch') }}
qualify run_date = max(run_date) over ()
