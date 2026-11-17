-- the pivot's max() is only safe if no first-party key has two prices for one metric
select run_date, platform, model_key, metric
from {{ source('raw', 'tokencanopy') }}
where variant = 'unknown'
  and platform in (select distinct platform from {{ ref('stg_tokencanopy__prices') }})
  and metric in ('input', 'output')
group by run_date, platform, model_key, metric
having count(distinct usd_per_1m) > 1
