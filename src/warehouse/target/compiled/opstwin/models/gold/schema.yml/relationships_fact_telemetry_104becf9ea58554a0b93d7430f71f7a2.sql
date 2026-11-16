
    
    

with child as (
    select sensor_key as from_field
    from "opstwin"."gold"."fact_telemetry"
    where sensor_key is not null
),

parent as (
    select sensor_key as to_field
    from "opstwin"."gold"."dim_sensor"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


