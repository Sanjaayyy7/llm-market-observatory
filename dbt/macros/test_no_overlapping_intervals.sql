{% test no_overlapping_intervals(model, key, from_col, to_col) %}
-- half-open intervals [from, to); a null `to` is open-ended
select a.{{ key }}
from {{ model }} a
join {{ model }} b
  on a.{{ key }} = b.{{ key }}
 and a.{{ from_col }} < b.{{ from_col }}
 and b.{{ from_col }} < coalesce(a.{{ to_col }}, 'infinity'::timestamptz)
{% endtest %}
