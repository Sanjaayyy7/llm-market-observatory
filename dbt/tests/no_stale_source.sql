select * from {{ ref('source_freshness') }} where is_stale
