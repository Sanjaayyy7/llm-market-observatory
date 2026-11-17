with platform_map(platform, provider) as (
    values
        ('OpenAI', 'openai'), ('Anthropic', 'anthropic'), ('Google AI Studio', 'google'),
        ('xAI', 'xai'), ('Mistral', 'mistral'), ('DeepSeek', 'deepseek'),
        ('Cohere', 'cohere'), ('Moonshot AI', 'moonshot')
),
-- rows differing only by the dropped region are duplicates; max() below collapses them (G1 FINDING)
firstparty as (
    select r.run_date, r.platform, m.provider, r.model_key, r.metric, r.usd_per_1m
    from {{ source('raw', 'tokencanopy') }} r
    join platform_map m using (platform)
    where r.variant = 'unknown' and r.metric in ('input', 'output')
)

select
    run_date,
    platform,
    provider,
    regexp_extract(model_key, '[^/]*$') as model_slug,
    max(usd_per_1m) filter (where metric = 'input') as in_per_mtok,
    max(usd_per_1m) filter (where metric = 'output') as out_per_mtok
from firstparty
group by run_date, platform, provider, model_key
