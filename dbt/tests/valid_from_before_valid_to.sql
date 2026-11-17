select model_key, valid_from, valid_to
from {{ ref('dim_model_price') }}
where valid_from >= valid_to
