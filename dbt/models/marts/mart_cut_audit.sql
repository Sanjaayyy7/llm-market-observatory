-- G4: provider-announced date vs the date LiteLLM recorded the cut (PRD §6 commit lag).
-- lag_days is announced - observed (UTC date); negative when the provider announced first.
select
    a.canonical_model_id,
    a.observed_ts,
    a.announced_date,
    date_diff('day', (a.observed_ts at time zone 'UTC')::date, a.announced_date) as lag_days,
    a.source_url,
    a.is_data_fix,
    a.verdict,
    -- G4 council P1: the kill-rate frame is the events the headline scores (top-tier first cut before censoring)
    s.canonical_model_id is not null as is_scored_event
from {{ ref('seed_cut_audit') }} a
join {{ ref('fct_price_change') }} c
    on c.canonical_model_id = a.canonical_model_id and c.change_ts = a.observed_ts
left join {{ ref('mart_launch_price_survival') }} s
    on s.canonical_model_id = a.canonical_model_id and s.first_cut_at = a.observed_ts
where c.is_cut and not c.is_correction
