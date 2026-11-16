{% macro raw_root() %}
{{ return(var('raw_root', '../tests/fixtures/raw' if target.name == 'ci' else '../data/raw')) }}
{% endmacro %}
