-- the pivot's max() is only safe if no first-party key has two prices for one metric
select run_date, platform, model_key, metric
from {{ source('raw', 'tokencanopy') }}
where variant = 'unknown'
  and platform in ('OpenAI', 'Anthropic', 'Google AI Studio', 'xAI', 'Mistral', 'DeepSeek', 'Cohere', 'Moonshot AI')
  and metric in ('input', 'output')
group by run_date, platform, model_key, metric
having count(distinct usd_per_1m) > 1
