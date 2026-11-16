
    
    

with all_values as (

    select
        metric as value_field,
        count(*) as n_records

    from "opstwin"."staging"."stg_telemetry"
    group by metric

)

select *
from all_values
where value_field not in (
    'temperature','humidity','power','water','vibration'
)


