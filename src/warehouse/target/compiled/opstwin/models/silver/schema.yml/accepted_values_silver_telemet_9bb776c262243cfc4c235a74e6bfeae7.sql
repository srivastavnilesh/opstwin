
    
    

with all_values as (

    select
        unit_normalized as value_field,
        count(*) as n_records

    from "opstwin"."silver"."silver_telemetry"
    group by unit_normalized

)

select *
from all_values
where value_field not in (
    'C','%','kW','L/min','mm/s'
)


