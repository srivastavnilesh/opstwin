with clean as (
    select sensor_id, value_normalized
    from {{ ref('int_telemetry_clean') }}
    where value_normalized is not null
),
med as (
    select sensor_id, median(value_normalized) as med_value
    from clean group by sensor_id
)
select
    c.sensor_id,
    m.med_value,
    median(abs(c.value_normalized - m.med_value)) as mad_value,
    count(*)                                      as n_obs
from clean c
join med m on m.sensor_id = c.sensor_id
group by c.sensor_id, m.med_value