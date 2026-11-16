
    
    

with all_values as (

    select
        status as value_field,
        count(*) as n_records

    from "opstwin"."silver"."silver_work_orders"
    group by status

)

select *
from all_values
where value_field not in (
    'OPEN','CLOSED'
)


